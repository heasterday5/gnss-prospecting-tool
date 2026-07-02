"""Live account research — the app researches the web at runtime.

Calls Claude (with server-side web search) to pull the account's actual
command-staff roster, the incumbent alerting vendor, and recent local
notification/evacuation events. Nothing is stored in the app; results are
cached in-process for 7 days per account.

Requires ANTHROPIC_API_KEY in Streamlit secrets (or the environment).
"""

import json
import os
import re

import streamlit as st

CACHE_TTL_SECONDS = 7 * 24 * 3600
DEFAULT_MODEL = "claude-opus-4-8"

RESULT_SPEC = """
Return ONLY a JSON object inside a ```json fenced block, with exactly this shape:
{
  "agency": {
    "official_name": str,
    "website": str or null,
    "email_domain": str or null,        // e.g. "fresno.gov"
    "email_pattern": str or null,       // e.g. "first.last@fresno.gov" — only if seen on a real address
    "main_phone": str or null
  },
  "contacts": [
    {
      "name": str,                      // real person, found in a public source
      "title": str,
      "division": str,                  // e.g. "Administration", "Patrol / Operations"
      "rank_order": int,                // 1 = highest rank; follow the hierarchy exactly
      "email": str or null,             // only if published; do NOT guess
      "email_guess": str or null,       // pattern-derived guess, only if email_pattern is known
      "phone": str or null,
      "source_url": str
    }
  ],
  "incumbent": {
    "vendor": str or null,              // current mass-notification/alerting vendor if documented
    "product": str or null,
    "evidence": str or null,            // one sentence, quotable
    "source_url": str or null,
    "contract_note": str or null        // renewal/procurement info if found
  },
  "recent_events": [
    {
      "year": int,
      "what_happened": str,             // one factual sentence
      "sales_relevance": str,           // one sentence: why a Genasys rep should care
      "source_url": str
    }
  ],
  "notes": str or null                  // anything else useful, 1-2 sentences
}
"""


def _get_api_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def is_configured() -> bool:
    return bool(_get_api_key())


def _parse_result(text: str) -> dict:
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    raw = m.group(1) if m else None
    if raw is None:
        # fall back to the outermost braces
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("no JSON object in research response")
        raw = text[start:end + 1]
    return json.loads(raw)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def research_account(account: str, county: str, state: str, segment: str,
                     hierarchy_text: str) -> dict:
    """Live-research one account. Cached 7 days per (account, county, state, segment)."""
    import anthropic

    client = anthropic.Anthropic(api_key=_get_api_key(), timeout=480.0, max_retries=1)
    model = None
    try:
        model = st.secrets.get("RESEARCH_MODEL")
    except Exception:
        pass
    model = model or DEFAULT_MODEL

    system = f"""You are a research assistant for the Genasys (public-safety technology) sales team.
You research US public-safety agencies using ONLY public web sources: the agency's own website,
staff directories, org charts, press releases, LinkedIn, local news, county alert-signup pages,
and council/board documents.

Hard rules:
- NEVER fabricate a name, email, or phone number. Every contact must come from a source you
  actually found, with its URL. If you cannot verify people, return an empty contacts list.
- Published emails go in "email". Pattern-derived guesses go in "email_guess" ONLY when you found
  the agency's real email pattern on at least one published address.
- Order contacts by this hierarchy, highest rank first — no skipping command staff, no burying
  division heads:
{hierarchy_text}
- For the incumbent alerting vendor, look at the jurisdiction's "emergency alerts" signup page
  (they usually name Everbridge, CodeRED, Rave, Genasys, etc.) and recent procurement news.
- For recent events, find notification failures, evacuations, or major incidents in or near the
  jurisdiction in the last ~5 years — with the year and what specifically went wrong or happened.
- Keep it tight: at most 12 contacts, at most 4 recent events. Speed matters."""

    prompt = (f"Research this account now:\n"
              f"- Account: {account}\n"
              f"- County: {county or 'unknown'}\n"
              f"- State: {state}\n"
              f"- Segment: {segment}\n\n"
              f"{RESULT_SPEC}")

    response = client.messages.create(
        model=model,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=system,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": prompt}],
    )

    # server-side tool loop can pause; continue until it finishes
    hops = 0
    messages = [{"role": "user", "content": prompt}]
    while response.stop_reason == "pause_turn" and hops < 4:
        messages = messages + [{"role": "assistant", "content": response.content}]
        response = client.messages.create(
            model=model,
            max_tokens=8000,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
            system=system,
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}],
            messages=messages,
        )
        hops += 1

    if response.stop_reason == "refusal":
        raise RuntimeError("Research request was declined — try rephrasing the account name.")

    text = "".join(b.text for b in response.content if b.type == "text")
    result = _parse_result(text)
    result["_model"] = model
    return result
