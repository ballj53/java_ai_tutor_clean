# views/dashboard.py

import time
import streamlit as st
from datetime import datetime

from utils.config import (
    SESSION_DURATION, CONDITIONS, SESSIONS, STUDY_INFO,
    SESSION_1_START, SESSION_2_START, SESSION_3_START
)

from utils.auth import logout_user, get_user_data
from utils.database import (
    save_session_start, save_message,
    get_session_status, get_next_session
)

from content.research_topics import get_research_topic

from client.ai_client import SimpleAIClient
import tutor_flow.flow_manager
# Lazy import to avoid circular dependency
# from tutor_flow.handlers import generate_initial_message


def render_dashboard():
    """Render the main dashboard showing session progress."""
    st.title(f"Welcome, {st.session_state.email}!")

    # Get user data and condition
    user_data = get_user_data(st.session_state.user_id)
    condition = user_data.get("condition", 1)
    condition_name = CONDITIONS.get(condition, "Unknown")

    st.session_state.condition = condition

    st.write("---")

    # Next session
    next_session = get_next_session(st.session_state.user_id)

    if next_session is None:
        st.success("🎉 You've completed all of the sessions!")
        st.balloons()
        st.write("Thank you for participating in our research study!")
        st.write("Your responses have been recorded.")

        if st.button("Logout"):
            logout_user()
            st.rerun()
        return

    # Session cards
    st.subheader("Your Sessions")

    for session_key in ["session_1", "session_2", "session_3"]:
        session_config = SESSIONS[session_key]
        session_id = session_config["id"]
        status = get_session_status(st.session_state.user_id, session_id)

        # Availability - time-based check
        start_date = datetime.strptime(session_config["start_date"], '%Y-%m-%d')
        is_available = datetime.now() >= start_date

        # Check prerequisite completion if required
        if is_available and "requires_completion" in session_config:
            required = session_config["requires_completion"]
            required_status = get_session_status(
                st.session_state.user_id,
                SESSIONS[required]["id"],  # use the actual required session
            )
            if required_status != "completed":
                is_available = False

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"### {session_config['name']}")
                st.write(session_config["description"])

            with col2:
                if status == "completed":
                    st.success("✅ Complete")
                elif status == "in_progress":
                    st.warning("⏸️ In Progress")
                elif not is_available:
                    st.info("🔒 Locked")
                else:
                    st.info("📝 Available")

            with col3:
                if status in ("completed",) or not is_available:
                    st.write("")
                else:
                    if st.button("Start", key=f"start_{session_id}", type="primary"):
                        start_session(session_id)
                        st.rerun()

            st.write("---")

    # Logout
    if st.button("Logout"):
        logout_user()
        st.rerun()

def start_session(session_id: str):
    """Initialize a learning session (all users use tutor flow)."""
    from tutor_flow.handlers import generate_initial_message

    topic = get_research_topic(session_id)
    condition = st.session_state.condition

    # Initialize AI client
    st.session_state.ai_client = SimpleAIClient()
    st.session_state.current_session_id = session_id

    # Save session start to database
    save_session_start(st.session_state.user_id, session_id, condition)

    # Initialize tutor flow for all conditions
    st.session_state.flow = tutor_flow.flow_manager.TutorFlow(
        topic.key
    )
    st.session_state.phase = "learning"
    st.session_state.start_time = time.time()
    st.session_state.session_active = True
    generate_initial_message(topic, condition)
