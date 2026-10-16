# routing/router.py

import streamlit as st

from routing.guards import login_required

# Views
from views.login import render_login_page
from views.dashboard import render_dashboard
from views.learning import render_learning_session
from views.quiz import render_quiz
from views.survey import render_survey_page
from views.complete import render_complete


def route():
    """
    Central routing function.
    Determines which view to show based on session state and URL params.
    """
    # ---------------------------------------------------------
    # DEBUG DASHBOARD (check first, before login)
    # ---------------------------------------------------------
    if st.query_params.get("debug") == "true":
        from utils.firebase_debug import render_debug_dashboard
        return render_debug_dashboard()
    
    # ---------------------------------------------------------
    # DATA EXPORT (for researchers)
    # ---------------------------------------------------------
    if st.query_params.get("export") == "true":
        from utils.data_export import render_admin_export
        return render_admin_export()
    
    # ---------------------------------------------------------
    # LOGIN GATE
    # ---------------------------------------------------------
    if not login_required():
        return render_login_page()

    # ---------------------------------------------------------
    # PHASE-BASED ROUTING
    # ---------------------------------------------------------
    phase = st.session_state.get("phase", "dashboard")

    if phase == "dashboard":
        return render_dashboard()

    if phase == "learning":
        return render_learning_session()

    if phase == "quiz":
        return render_quiz()

    if phase == "survey":
        return render_survey_page()

    if phase == "complete":
        return render_complete()

    # ---------------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------------
    return render_dashboard()

