"""Rep identity captured once in the sidebar, reused across email drafts."""

import streamlit as st


def rep_identity_sidebar() -> dict:
    with st.sidebar:
        with st.expander("Your signature (for email drafts)"):
            name = st.text_input("Name", value=st.session_state.get("rep_name", ""), key="_rep_name")
            title = st.text_input("Title", value=st.session_state.get("rep_title", ""), key="_rep_title")
            phone = st.text_input("Phone", value=st.session_state.get("rep_phone", ""), key="_rep_phone")
            st.session_state["rep_name"] = name
            st.session_state["rep_title"] = title
            st.session_state["rep_phone"] = phone
    return {
        "sender_name": st.session_state.get("rep_name", ""),
        "sender_title": st.session_state.get("rep_title", ""),
        "sender_phone": st.session_state.get("rep_phone", ""),
    }
