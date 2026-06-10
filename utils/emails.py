"""Email template rendering with {{token}} placeholders."""

import re
import urllib.parse


def render(template: dict, values: dict) -> dict:
    """Fill {{tokens}} in subject/body. Unfilled tokens become [BRACKETED PROMPTS]."""
    def fill(text: str) -> str:
        def sub(m):
            key = m.group(1).strip()
            val = values.get(key, "")
            if val:
                return str(val)
            return "[" + key.replace("_", " ").upper() + "]"
        return re.sub(r"\{\{(\w+)\}\}", sub, text)

    return {"subject": fill(template["subject"]), "body": fill(template["body"])}


def tokens_in(template: dict) -> list:
    found = []
    for text in (template.get("subject", ""), template.get("body", "")):
        for m in re.findall(r"\{\{(\w+)\}\}", text):
            if m not in found:
                found.append(m)
    return found


def mailto_link(subject: str, body: str, to: str = "") -> str:
    return (
        f"mailto:{to}?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )


# Tokens auto-filled from Pathfinder context rather than typed by the rep
AUTO_TOKEN_HINTS = {
    "state": "Selected state",
    "saa_name": "State EM agency name (from verified directory)",
    "sender_name": "Your name",
    "sender_title": "Your title",
    "sender_phone": "Your phone",
}
