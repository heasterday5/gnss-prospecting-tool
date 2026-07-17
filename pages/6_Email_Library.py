"""Email Library — every outreach template, fillable and copy-ready."""

import streamlit as st
from utils.auth import check_password
check_password()

from utils.styles import md_html, inject_css, sidebar_brand, page_header
from utils.data_loader import load_email_templates
from utils.emails import render, tokens_in
from utils.identity import rep_identity_sidebar

inject_css()
sidebar_brand()
sender = rep_identity_sidebar()

page_header(
    "What to say",
    "Email Library",
    "Signal-matched outreach, the post-discovery procurement package, and the Lexipol handoff. "
    "Fill the bracketed fields, copy, send. Set your signature once in the sidebar.",
)

templates = load_email_templates()

names = [t["name"] for t in templates]
chosen = st.selectbox("Choose a template", names)
tmpl = templates[names.index(chosen)]

md_html(f"""
<div class="gn-card teal">
    <div class="gn-label">Audience</div>
    <div class="gn-value">{tmpl['audience']}</div>
    <div class="gn-label" style="margin-top:0.5rem;">When to use</div>
    <div class="gn-value">{tmpl['when_to_use']}</div>
</div>
""")

vals = dict(sender)
needed = [t for t in tokens_in(tmpl) if not vals.get(t)]
if needed:
    st.markdown('<div class="gn-label">Fill in the details (blank fields become [PROMPTS] you can edit after pasting)</div>',
                unsafe_allow_html=True)
    tcols = st.columns(min(3, max(1, len(needed))))
    for i, tok in enumerate(needed):
        with tcols[i % len(tcols)]:
            vals[tok] = st.text_input(tok.replace("_", " ").title(), key=f"lib_{tmpl['id']}_{tok}")

rendered = render(tmpl, vals)
st.text_input("Subject", value=rendered["subject"], disabled=True)
st.code(rendered["body"], language=None)
st.caption(f"**Follow-up guidance:** {tmpl.get('follow_up', '')}")
