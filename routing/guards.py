# routing/guards.py

import streamlit as st


def login_required() -> bool:
    """Return True if the user is logged in."""
    return bool(st.session_state.get("logged_in"))


def admin_only() -> bool:
    """Return True if the logged-in user is an admin."""
    return bool(st.session_state.get("is_admin", False))
