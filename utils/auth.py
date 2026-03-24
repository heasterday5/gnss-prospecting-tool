"""Password gate using Streamlit Secrets (never hardcoded in code)."""

import streamlit as st


def check_password() -> bool:
    """Show login screen if not authenticated. Returns True if user is logged in."""
    if st.session_state.get("authenticated"):
        return True

    st.set_page_config(page_title="Login | GNSS", page_icon="🔒", layout="centered")

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
        <h1 style="color:#163443;margin:0;">🎯 GNSS</h1>
        <p style="color:#56C8DA;font-size:1.1rem;">Sales Prospecting Tool</p>
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
