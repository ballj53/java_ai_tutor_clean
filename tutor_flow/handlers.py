# tutor_flow/handlers.py
"""
Message handlers for the tutoring flow.
SIMPLIFIED: Clean flow, let AI handle conversation nuance.
"""

import time
import streamlit as st
from utils.database import save_message, save_scaffold_progress


def generate_initial_message(topic, condition):
    """
    Generate the initial learning message for scaffolded conditions.
    Called automatically when session starts.
    """
    from tutor_flow.step_guide import StepGuide

    session_id = st.session_state.current_session_id

    # Build system prompt
    system_prompt = (
        f"You are a friendly, encouraging CS tutor teaching {topic.name}.\n"
        "Be conversational, warm, and clear. Keep responses focused and under 150 words."
    )

    # Get the metaphor prompt
    metaphor_prompt = StepGuide.get_metaphor_prompt(topic)

    # Generate the initial message
    try:
        initial_message = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=metaphor_prompt,
            temperature=0.9,
        )
    except Exception as e:
        print(f"ERROR generating initial message: {e}")
        initial_message = (
            f"Hello! Let's learn about {topic.name}.\n\n"
            f"**What we'll cover:** {topic.concept}\n\n"
            f"{topic.metaphor_prompt}\n\n"
            "What does this remind you of from your own experience?"
        )

    # Add to flow and save
    st.session_state.flow.add_message("assistant", initial_message)
    save_message(
        st.session_state.user_id,
        session_id,
        "assistant",
        initial_message,
        step=st.session_state.flow.current_step.value,
    )
    print(f"INITIAL MESSAGE generated for {topic.name}")


def handle_user_message_scaffolded(user_input: str):
    """
    Handle user message for scaffolded conditions (1 & 2).
    Simple flow: record message → check advancement → generate response.
    """
    from tutor_flow.step_guide import StepGuide
    from tutor_flow.steps import ScaffoldStep
    from content.research_topics import get_research_topic
    from content.visuals import get_topic_visual

    flow = st.session_state.flow
    topic = get_research_topic(st.session_state.current_session_id)
    condition = st.session_state.condition
    session_id = st.session_state.current_session_id

    # =========================================================
    # 1. RECORD USER MESSAGE
    # =========================================================
    flow.add_message("user", user_input)
    save_message(st.session_state.user_id, session_id, "user", user_input)

    print(f"\n{'=' * 50}")
    print(f"USER: {user_input}")
    print(f"STEP: {flow.current_step.value} (AI messages in step: {flow.step_message_count})")

    # =========================================================
    # 2. CHECK FOR SESSION END CONDITIONS
    # =========================================================

    # Time-based end
    start_time = st.session_state.get('start_time', time.time())
    elapsed_minutes = (time.time() - start_time) / 60
    if elapsed_minutes >= 15:
        _end_session("time", flow, session_id)
        return

    # Natural completion (after reflection)
    if st.session_state.get('ready_for_quiz', False):
        _end_session("complete", flow, session_id)
        return

    # =========================================================
    # 3. CHECK FOR STEP ADVANCEMENT
    # =========================================================
    advanced_to_visual = False

    if flow.should_advance_step(user_input):
        old_step = flow.current_step
        flow.advance_step()
        save_scaffold_progress(st.session_state.user_id, session_id, flow.current_step.value)
        print(f"ADVANCED: {old_step.value} → {flow.current_step.value}")

        if flow.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            advanced_to_visual = True

        # Check if we completed reflection
        if old_step == ScaffoldStep.REFLECTION and flow.completed:
            st.session_state.ready_for_quiz = True
            # Don't return yet - let AI give final response

    # =========================================================
    # 4. HANDLE VISUAL DIAGRAM (special case - pre-built content)
    # =========================================================
    if advanced_to_visual:
        _show_visual_diagram(flow, topic, session_id)
        return

    # =========================================================
    # 5. GENERATE AI RESPONSE
    # =========================================================
    _generate_response(flow, topic, condition, session_id, user_input)

    # =========================================================
    # 6. CHECK IF QUIZ READY (after AI responds)
    # =========================================================
    if st.session_state.get('ready_for_quiz', False):
        # AI just gave final response, now we can transition
        print("QUIZ: Ready flag set, will transition on next interaction")


def _show_visual_diagram(flow, topic, session_id):
    """Show the visual diagram for the current topic."""
    from content.visuals import get_topic_visual

    visual = get_topic_visual(st.session_state.current_session_id)

    if topic.key == 'arraylist':
        walkthrough = (
            "Let me walk you through this:\n"
            "- **Step 1**: The old array is full (4/4 elements)\n"
            "- **Step 2**: Create a new, larger array (capacity 8)\n"
            "- **Step 3**: Copy all elements to the new array\n"
            "- **Step 4**: Add the new element (E)\n\n"
            "Does this help you see how the resizing works?"
        )
    elif topic.key == 'recursion':
        walkthrough = (
            "Let me walk you through this:\n"
            "- **Building up**: Each recursive call adds a frame to the stack\n"
            "- **Base case (n=1)**: This is the 'stop sign' - recursion stops here\n"
            "- **Unwinding**: Each frame returns its value back up the chain\n\n"
            "Can you see how the stack builds up and then unwinds?"
        )
    elif topic.key == 'queue':
        walkthrough = (
            "Let me walk you through this:\n"
            "- **Queue (top)**: Fair line — first in, first out. `poll()` always takes from the front, `offer()` adds to the back\n"
            "- **peek()**: Lets you look at who's next without removing them\n"
            "- **Priority Queue (bottom)**: Arrival order is thrown out — the most urgent item jumps to the front\n"
            "- **Min-heap**: Java's default — smallest number = highest priority\n\n"
            "Does this diagram help you see the difference between the two?"
        )
    else:
        walkthrough = "Does this diagram help you understand how it works?"

    visual_message = (
        "Great! Here's a visual diagram showing exactly how this works:\n\n"
        f"📊 **Visual Diagram:**\n{visual}\n\n"
        f"{walkthrough}"
    )

    flow.add_message("assistant", visual_message)
    save_message(st.session_state.user_id, session_id, "assistant", visual_message,
                 step=flow.current_step.value)
    print(f"VISUAL shown for {topic.key}")


def _generate_response(flow, topic, condition, session_id, user_input):
    """Generate an AI response for the current step."""
    from tutor_flow.step_guide import StepGuide

    # Get the response prompt (includes context and instructions)
    response_prompt = StepGuide.get_response_prompt(
        topic=topic,
        current_step=flow.current_step,
        user_input=user_input,
        context_messages=flow.get_recent_context(5),
    )

    print(f"PROMPT:\n{response_prompt[:200]}...")

    # Build system prompt
    system_prompt = (
        f"You are a helpful, encouraging CS tutor teaching {topic.name}.\n"
        "Be conversational and clear. Validate student answers explicitly.\n"
        "Keep responses focused and under 150 words."
    )

    # Build conversation history
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in flow.get_recent_context(5)[:-1]
    ]

    # Generate response
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=response_prompt,
            conversation_history=conversation_history,
        )
    except Exception as e:
        print(f"ERROR: {e}")
        response = "I'm having trouble responding. Could you try rephrasing that?"

    # Record response
    flow.add_message("assistant", response)
    save_message(st.session_state.user_id, session_id, "assistant", response,
                 step=flow.current_step.value)
    print(f"AI: {response[:100]}...")


def _end_session(reason, flow, session_id):
    """End the session and transition to quiz."""
    if st.session_state.get('quiz_ready', False):
        return

    if reason == "time":
        final_message = (
            "⏰ Time's up! Great work today. Let's see what you learned - quiz time!"
        )
    else:
        final_message = (
            "🎉 Excellent work! You've completed the lesson. Ready for the quiz!"
        )

    flow.add_message("assistant", final_message)
    save_message(st.session_state.user_id, session_id, "assistant", final_message,
                 step=flow.current_step.value)

    st.session_state.quiz_ready = True
    print(f"SESSION ENDED: {reason}")
    st.rerun()


def handle_user_message_direct(user_input: str):
    """Handle user message for direct chat condition (3)."""
    from content.research_topics import get_research_topic

    topic = get_research_topic(st.session_state.current_session_id)
    session_id = st.session_state.current_session_id

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": time.time(),
    })
    save_message(st.session_state.user_id, session_id, "user", user_input)

    # Check time
    start_time = st.session_state.get('start_time', time.time())
    elapsed_minutes = (time.time() - start_time) / 60

    if elapsed_minutes >= 15:
        if not st.session_state.get('quiz_ready', False):
            final_message = "Time's up! Let's test your knowledge with a quiz."
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_message,
                "timestamp": time.time(),
            })
            save_message(st.session_state.user_id, session_id, "assistant", final_message)
            st.session_state.quiz_ready = True
            st.rerun()
        return

    # Build conversation history
    conversation_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-10:]
    ]

    # System prompt
    system_prompt = (
        f"You are a helpful assistant teaching {topic.name} in Java.\n"
        "Be clear, include code examples when helpful, and be concise."
    )

    # Generate response
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=user_input,
            conversation_history=conversation_history,
        )
    except Exception:
        response = "I'm having trouble responding. Could you try rephrasing?"

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": time.time(),
    })
    save_message(st.session_state.user_id, session_id, "assistant", response)