# session/session_manager.py

import time
import streamlit as st

from content.research_topics import get_research_topic
from tutor_flow.flow_manager import TutorFlow
# Lazy import to avoid circular dependency
# from tutor_flow.handlers import generate_initial_message
from utils.database import save_session_start, save_message
from client.ai_client import SimpleAIClient


def start_session(session_id: str):
    """Initialize a learning session."""
    from tutor_flow.handlers import generate_initial_message
    
    topic = get_research_topic(session_id)
    condition = st.session_state.condition

    # Initialize AI client
    st.session_state.ai_client = SimpleAIClient()
    st.session_state.current_session_id = session_id

    # Save session start to database
    save_session_start(st.session_state.user_id, session_id, condition)

    # ---------------------------------------------------------
    # CONDITION 1 & 2 — SCAFFOLDED
    # ---------------------------------------------------------
    if condition in [1, 2]:
        st.session_state.flow = TutorFlow(topic.key)

        # Direct scaffolded learning
        st.session_state.phase = "learning"
        st.session_state.start_time = time.time()
        st.session_state.session_active = True
        generate_initial_message(topic, condition)

    # ---------------------------------------------------------
    # CONDITION 3 — DIRECT CHAT
    # ---------------------------------------------------------
    else:
        st.session_state.phase = "learning"
        st.session_state.start_time = time.time()
        st.session_state.session_active = True
        st.session_state.messages = []

        welcome = (
            f"Hello! I'm here to answer your questions about {topic.name}. "
            f"What would you like to know?"
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome,
            "timestamp": time.time(),
        })

        save_message(st.session_state.user_id, session_id, "assistant", welcome)