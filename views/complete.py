# views/complete.py

import streamlit as st
from utils.database import get_next_session


def render_complete():
    """Render the session completion page."""

    st.title("✅ Session Complete!")
    st.success("Thank you for completing this session!")

    # Check if there's another session
    next_session = get_next_session(st.session_state.user_id)

    if next_session:
        st.write("You have at least one more session to complete later in the semester.")
        st.write("We'll let you know when it's time!")
    else:
        st.balloons()
        st.write("You've completed all sessions!")
        st.write("Thank you for participating in our research!")

    # Back to dashboard button
    if st.button("Back to Dashboard", type="primary"):
        # Reset session-specific state
        st.session_state.current_session_id = None
        st.session_state.phase = "dashboard"
        st.session_state.session_active = False
        st.session_state.flow = None
        st.session_state.messages = []
        st.session_state.quiz_answers = {}
        st.session_state.survey_responses = {}
        st.session_state.quiz_submitted = False

        st.rerun()