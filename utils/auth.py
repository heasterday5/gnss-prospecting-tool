"""Password gate using Streamlit Secrets (never hardcoded in code)."""

import streamlit as st


def check_password() -> bool:
    """Show login screen if not authenticated. Returns True if user is logged in."""
    if st.session_state.get("authenticated"):
        return True

    st.set_page_config(page_title="Login | Genasys Funding Intelligence",
                       page_icon="🛡️", layout="centered")

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    </style>
    <div style="text-align:center;padding:2.5rem 0 1.2rem;">
        <div style="font-size:2rem;font-weight:900;letter-spacing:0.18em;color:#163443;">
            GENASYS<span style="color:#ABCF38;">.</span>
        </div>
        <div style="font-size:0.8rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#56C8DA;margin-top:4px;">
            Funding Intelligence
        </div>
        <div style="color:#5A6B75;font-size:0.95rem;margin-top:10px;">Ready when it matters</div>
        <div style="width:64px;height:4px;background:linear-gradient(90deg,#ABCF38,#56C8DA);margin:1rem auto 0;border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        password = st.text_input("Password", type="password", placeholder="Enter team password")
        submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

        if submitted:
            if password == st.secrets["app_password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

    st.caption("Contact your team admin if you don't have the password.")
    st.stop()
    return False
