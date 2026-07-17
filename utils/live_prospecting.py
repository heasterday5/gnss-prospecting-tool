"""Live territory prospecting — state + org type → ICP-ranked target list.

Uses the same Claude + web-search backend as live_research, but at territory
scale: identifies the 15-20 organizations in a state that best match the
Genasys ICP for the chosen segment, scores each against the ICP's best-fit
attributes and caution signals, and explains the ranking with sources.
Decision-maker contacts are then researched per-organization via
live_research.research_account (already built, cached 7 days).

Requires ANTHROPIC_API_KEY in Streamlit secrets (or the environment).
"""

import json

import streamlit as st

from utils.data_loader import load_deployments, load_incidents, get_state_row
from utils.live_research import _get_api_key, _parse_result, is_configured  # noqa: F401  (re-exported)

CACHE_TTL_SECONDS = 7 * 24 * 3600
DEFAULT_MODEL = "claude-opus-4-8"

RESULT_SPEC = """
Return ONLY a JSON object inside a ```json fenced block, with exactly this shape:
{
  "market_notes": str,            // 2-3 sentences: this state's landscape for this segment
  "prospects": [
    {
      "rank": int,                // 1 = best fit
      "name": str,                // official entity name, e.g. "Pierce County Emergency Management"
      "county": str or null,      // county it sits in, with suffix, e.g. "Pierce County"
      "population_served": str or null,   // e.g. "930,000" — jurisdiction population if known
      "fit_score": int,           // 0-100 against the ICP below
      "tier": str,                // "Prime" (top ~5) | "Strong" | "Worth a look"
      "why_fit": [str],           // 2-5 bullets; each must tie a FACT you found to a named ICP attribute
      "caution_flags": [str],     // ICP caution signals you actually observed; [] if none
      "incumbent": str or null,   // current alerting/comms vendor if documented
      "recent_events": str or null,  // one line: disasters, near-misses, unrest — with years
      "product_angle": str,       // one sentence: which Genasys product leads here and why
      "source_urls": [str]        // up to 3 URLs backing the above
    }
  ]
}
"""


def _grounding(state: str, icp: dict) -> str:
    """Assemble what we already know about this state from the app's datasets."""
    lines = []
    row = get_state_row(state)

    try:
        states_df = __import__("utils.data_loader", fromlist=["load_states"]).load_states()
        srow = states_df[states_df["state"] == state]
        if not srow.empty:
            s = srow.iloc[0]
            lines.append(f"State hazard profile: {s['key_hazards']}")
    except Exception:
        pass

    dep = load_deployments()
    dep_state = dep[dep["state"] == state]
    gen = dep_state[dep_state["vendor"] == "Genasys"]
    comp = dep_state[dep_state["vendor"] != "Genasys"]
    if not gen.empty:
        lines.append("Known Genasys customers in-state (reference accounts — a neighbor using "
                     "Genasys raises a prospect's fit): "
                     + "; ".join(gen["jurisdiction"].head(12)))
    if not comp.empty:
        lines.append("Known competitor deployments in-state (displacement targets, esp. near "
                     "contract renewal): "
                     + "; ".join(f"{r.jurisdiction} ({r.vendor})" for r in comp.head(12).itertuples()))

    inc = load_incidents()
    inc_state = inc[inc["state"] == state]
    if not inc_state.empty:
        lines.append("Documented notification/evacuation incidents in-state (pain = fit): "
                     + "; ".join(f"{r.place} {r.year} ({r.incident_type})"
                                 for r in inc_state.head(10).itertuples()))
    if row is not None:
        lines.append(f"State EM agency: {row['Agency Name']}")
    return "\n".join(f"- {l}" for l in lines) if lines else "- (no prior data on this state)"


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def find_prospects(state: str, icp_id: str, icp_json: str, _progress=None) -> dict:
    """Rank the 15-20 best-fit prospects in a state for one ICP segment.

    Cached 7 days per (state, icp_id, icp_json). icp_json is passed as a string
    so the cache key stays stable and hashable.
    """
    import anthropic

    icp = json.loads(icp_json)

    def note(msg):
        if _progress:
            try:
                _progress(msg)
            except Exception:
                pass

    client = anthropic.Anthropic(api_key=_get_api_key(), timeout=600.0, max_retries=1)
    model = None
    try:
        model = st.secrets.get("RESEARCH_MODEL")
    except Exception:
        pass
    model = model or DEFAULT_MODEL

    best_fit_text = "\n".join(
        f"{group}:\n" + "\n".join(f"  - {item}" for item in items)
        for group, items in icp["best_fit"].items()
    )
    caution_text = "\n".join(f"  - {c}" for c in icp["caution_signals"])

    system = f"""You are a territory-planning analyst for the Genasys (public-safety technology)
sales team. Your job: given a US state and a target segment, identify the 15-20 organizations
that BEST match the Ideal Customer Profile below, and rank them by fit. Use ONLY public web
sources: government websites, hazard mitigation plans, news coverage, census data, procurement
records, alert-signup pages.

THE IDEAL CUSTOMER PROFILE — {icp['label']} (products: {icp['products']}):
Best-fit attributes (more matches = higher fit_score):
{best_fit_text}

Caution signals (each observed one drags the score down; disqualify on strong evidence):
{caution_text}

Scoring rules:
- fit_score reflects EVIDENCE, not vibes: every why_fit bullet must pair a verifiable fact
  (population, hazard exposure, a named incident, an expiring contract, a modernization project)
  with the ICP attribute it satisfies.
- Population thresholds in the ICP are real gates: do not rank entities below them unless
  another attribute is overwhelming (then flag it).
- An entity already using Genasys products is NOT a prospect — exclude it (it may appear in the
  grounding data as a reference account).
- Spread across the state; do not just list the 20 biggest cities. The BEST fit often includes
  mid-size counties with severe hazard exposure or a documented notification failure.
- SPEED: at most 12 searches. Lean on statewide sources first (state hazard mitigation plan,
  news roundups, census lists, statewide vendor/procurement stories) rather than searching
  one entity at a time. Stop when you can rank confidently.
{RESULT_SPEC}"""

    prompt = (f"Build the ranked prospect list now.\n"
              f"- State: {state}\n"
              f"- Segment: {icp['label']} (typical entities: {icp['entity_examples']})\n\n"
              f"What we already know (from our own verified datasets — use it, it's reliable):\n"
              f"{_grounding(state, icp)}\n\n"
              f"Return 15-20 prospects, ranked, in the exact JSON shape specified.")

    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 12}]
    messages = [{"role": "user", "content": prompt}]
    searches = 0

    def run_streamed(msgs):
        nonlocal searches
        with client.messages.stream(
            model=model,
            max_tokens=20000,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            system=system,
            tools=tools,
            messages=msgs,
        ) as stream:
            wrote = False
            for event in stream:
                if event.type == "content_block_start":
                    btype = event.content_block.type
                    if btype == "server_tool_use":
                        searches += 1
                        note(f"🔎 Statewide sweep — search {searches} of ~12 "
                             f"(hazards, incidents, contracts, modernization projects)…")
                    elif btype == "web_search_tool_result":
                        note(f"📄 Reading results of search {searches}…")
                    elif btype == "text" and not wrote:
                        wrote = True
                        note("🧮 Scoring candidates against the ICP and ranking…")
            return stream.get_final_message()

    note(f"🧭 Mapping the {state} market for {icp['label']} — this takes 2-4 minutes, "
         f"and the result is cached for a week…")
    response = run_streamed(messages)

    hops = 0
    while response.stop_reason == "pause_turn" and hops < 5:
        note("↩️ Continuing the sweep (extra research round)…")
        messages = messages + [{"role": "assistant", "content": response.content}]
        response = run_streamed(messages)
        hops += 1

    if response.stop_reason == "refusal":
        raise RuntimeError("The research request was declined — try a different segment/state.")

    note("✅ Ranking complete — rendering the target list…")
    text = "".join(b.text for b in response.content if b.type == "text")
    result = _parse_result(text)
    result["_model"] = model
    # normalize + sort defensively
    prospects = result.get("prospects") or []
    for i, p in enumerate(prospects):
        p.setdefault("rank", i + 1)
        p.setdefault("fit_score", 0)
        p.setdefault("tier", "Worth a look")
        p.setdefault("why_fit", [])
        p.setdefault("caution_flags", [])
    result["prospects"] = sorted(prospects, key=lambda p: p["rank"])
    return result
