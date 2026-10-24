"""
Manages the scaffolded tutoring flow.
SIMPLIFIED: Trust the AI to handle conversation flow within each step.
Advancement is based on simple rules, not complex state tracking.
"""

from __future__ import annotations
from typing import List
from .steps import (
    ScaffoldStep,
    ConversationMessage,
    RoleType,
    is_student_question,
    has_help_signal,
    has_ready_signal,
)
import re

class TutorFlow:
    """
    Manages the scaffolded tutoring flow.
    Simple state machine - AI handles the nuance within each step.
    """

    STANDARD_STEPS: List[ScaffoldStep] = [
        ScaffoldStep.INITIAL_METAPHOR,
        ScaffoldStep.STUDENT_METAPHOR,
        ScaffoldStep.VISUAL_DIAGRAM,
        ScaffoldStep.CODE_STRUCTURE,
        ScaffoldStep.CODE_USAGE,
        ScaffoldStep.PRACTICE,
        ScaffoldStep.REFLECTION,
    ]

    ADAPTIVE_STEPS: List[ScaffoldStep] = [
        ScaffoldStep.INITIAL_METAPHOR,
        ScaffoldStep.STUDENT_METAPHOR,
        ScaffoldStep.VISUAL_DIAGRAM,
        ScaffoldStep.CODE_STRUCTURE,
        ScaffoldStep.CODE_USAGE,
        ScaffoldStep.WORKED_EXAMPLE,
        ScaffoldStep.GUIDED_PROBLEM,
        ScaffoldStep.PRACTICE,
        ScaffoldStep.REFLECTION,
    ]

    def __init__(self, topic_key: str, is_adaptive: bool = None, user_id: str = None) -> None:
        self.topic_key: str = topic_key

        # Resolve user_id from argument or Streamlit session_state
        if user_id is None:
            try:
                import streamlit as st
                user_id = getattr(st.session_state, "user_id", None)
            except Exception:
                user_id = None

        # -------------------------------------------------------------
        # ADAPTIVE SELECTION MECHANISM
        # The engine determines whether this lesson receives 2 extra steps
        # -------------------------------------------------------------
        if is_adaptive is None:
            if user_id:
                try:
                    from utils.database import is_adaptive_scaffold_eligible
                    is_adaptive = is_adaptive_scaffold_eligible(user_id, topic_key)
                except Exception:
                    is_adaptive = False
            else:
                is_adaptive = False

        self.is_adaptive: bool = bool(is_adaptive)
        self.lesson_tier: str = "high" if self.is_adaptive else "regular"
        self.duration_seconds: int = 20 * 60 if self.is_adaptive else 15 * 60
        self.duration_minutes: int = 20 if self.is_adaptive else 15
        self.steps: List[ScaffoldStep] = self.ADAPTIVE_STEPS if self.is_adaptive else self.STANDARD_STEPS
        self.current_step: ScaffoldStep = ScaffoldStep.INITIAL_METAPHOR
        self.messages: List[ConversationMessage] = []
        self.step_message_count: int = 0
        self.completed: bool = False

        # -------------------------------------------------------------
        # ENGINE ACCOUNTABILITY AUDIT
        # The engine that selects the lesson tier writes it to the database
        # -------------------------------------------------------------
        if user_id:
            try:
                from utils.database import record_lesson_tier
                record_lesson_tier(user_id, topic_key, self.lesson_tier)
            except Exception as e:
                print(f"[ENGINE AUDIT ERROR] Could not record lesson tier: {e}")

    def add_message(self, role: RoleType, content: str) -> None:
        """Append a message tagged with the current scaffold step."""
        msg = ConversationMessage(
            role=role,
            content=content,
            step=self.current_step,
        )
        self.messages.append(msg)
        if role == "assistant":
            self.step_message_count += 1

    def get_recent_context(self, n: int = 5) -> List[ConversationMessage]:
        """Return the last n messages for prompt context."""
        if n <= 0:
            return []
        return self.messages[-n:]

    def should_advance_step(self, user_message: str) -> bool:
        """
        Simple advancement rules. We trust the AI to:
        - Ask appropriate questions
        - Validate answers
        - Guide the student through each step

        We advance when student clearly signals readiness or answers substantively,
        while shielding students who ask questions or express confusion from being prematurely pushed forward.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())

        # Allow for forced step advancement with secret command (last resort if stuck)
        if user_lower == "force_advance_step":
            return True

        has_ready = has_ready_signal(user_lower)
        has_help = has_help_signal(user_lower)

        def is_advance_request() -> bool:
            advance_patterns = [
                r"what('?s| is) next",
                r"(let'?s|can we|shall we) (keep going|move on|continue|proceed|advance)",
                r"keep going",
                r"move on",
                r"next step",
                r"ready to (move on|continue|advance|keep going)",
                r"what do we do next",
            ]
            return any(re.search(pat, user_lower) for pat in advance_patterns)

        def is_inquiring_or_confused() -> bool:
            """Returns True if the student asked a genuine question or signaled confusion."""
            if has_help:
                return True
            if is_student_question(user_message):
                # Analogies like 'Like buying a bigger backpack?' or 'Maybe like a suitcase?'
                if any(user_lower.startswith(prefix) for prefix in ["like ", "maybe like ", "kind of like "]) and word_count >= 3:
                    return False
                # Tagged guesses like 'it doubles to 16, right?' or 'line 2 is the base case, correct?'
                is_tagged_guess = any(user_lower.endswith(tag) for tag in ["right?", "correct?", "yeah?", "yes?"]) and word_count >= 5
                return not is_tagged_guess
            return False

        def signals_ready() -> bool:
            # Check for ready signals, but not if they also signal confusion or questions
            return has_ready and not is_inquiring_or_confused()

        def gave_substantive_answer() -> bool:
            # Student gave a real answer (not an advance request, and not a confused question/request for help)
            if is_advance_request() or is_inquiring_or_confused():
                return False
            return word_count >= 4

        # ============================================================
        # STEP 1: INITIAL_METAPHOR → STUDENT_METAPHOR
        # Advance after student gives their metaphor or thoughts
        # ============================================================
        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            # If student asked a question or is confused, let tutor explain first
            if is_inquiring_or_confused():
                return self.step_message_count >= 4
            # Advance once student shares a metaphor/response (at least 5 characters or 2+ words)
            return len(user_message.strip()) > 5 or word_count >= 2

        # ============================================================
        # STEP 2: STUDENT_METAPHOR → VISUAL_DIAGRAM
        # Student shared metaphor, AI responded, student ready for visual
        # ============================================================
        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            if signals_ready() or gave_substantive_answer():
                return True
            # Soft cap: after 3 AI messages, advance if not asking questions
            if self.step_message_count >= 3:
                return True
            return False

        # ============================================================
        # STEP 3: VISUAL_DIAGRAM → CODE_STRUCTURE
        # Visual shown, student indicates understanding or readiness
        # ============================================================
        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            if signals_ready() or gave_substantive_answer():
                return True
            # Soft cap: after 3 AI messages, advance if not asking questions
            if self.step_message_count >= 3:
                return True
            return False

        # ============================================================
        # STEP 4: CODE_STRUCTURE → CODE_USAGE
        # AI shows code, student answers question OR says ready
        # ============================================================
        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            # On first message, student must answer the code question (cannot just skip by asking to advance)
            if self.step_message_count == 1:
                return gave_substantive_answer()
            # After 2+ messages, ready signal or substantive answer advances
            if signals_ready() or gave_substantive_answer():
                return True
            # Soft cap: after 3 AI messages, advance if not asking questions
            if self.step_message_count >= 3:
                return True
            return False

        # ============================================================
        # STEP 5: CODE_USAGE → PRACTICE
        # AI shows usage, student answers question OR says ready
        # ============================================================
        if self.current_step == ScaffoldStep.CODE_USAGE:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            # On first message, student must answer the usage question
            if self.step_message_count == 1:
                return gave_substantive_answer()
            # After 2+ messages, ready signal or substantive answer advances
            if signals_ready() or gave_substantive_answer():
                return True
            # Soft cap: after 3 AI messages, advance if not asking questions
            if self.step_message_count >= 3:
                return True
            return False

        # ============================================================
        # ADAPTIVE STEP 5a: WORKED_EXAMPLE → GUIDED_PROBLEM
        # AI walks through worked example, student answers question or says ready
        # ============================================================
        if self.current_step == ScaffoldStep.WORKED_EXAMPLE:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            if self.step_message_count == 1:
                return gave_substantive_answer()
            if signals_ready() or gave_substantive_answer():
                return True
            if self.step_message_count >= 3:
                return True
            return False

        # ============================================================
        # ADAPTIVE STEP 5b: GUIDED_PROBLEM → PRACTICE
        # AI shows guided problem/TODOs, student answers/completes blanks
        # ============================================================
        if self.current_step == ScaffoldStep.GUIDED_PROBLEM:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 5
            if self.step_message_count == 1:
                return gave_substantive_answer()
            if signals_ready() or gave_substantive_answer():
                return True
            if self.step_message_count >= 4:
                return True
            return False

        # ============================================================
        # STEP 6: PRACTICE → REFLECTION
        # AI gives problem → student answers → AI validates (asks ready to summarize?) → student responds
        # ============================================================
        if self.current_step == ScaffoldStep.PRACTICE:
            # Hard cap: after 5 AI messages in practice, advance so student never gets trapped (protects 15-min study limit)
            if self.step_message_count >= 5:
                return True

            # If student is asking clarifying questions, do not advance
            if is_inquiring_or_confused():
                return False

            # Tutor must have validated the practice problem and asked "Ready to summarize?"
            tutor_asked_summary = any(
                m.role == "assistant"
                and (m.step == ScaffoldStep.PRACTICE or getattr(m.step, "value", m.step) == ScaffoldStep.PRACTICE.value)
                and "summarize" in m.content.lower()
                for m in self.messages
            )
            if not tutor_asked_summary:
                # Do NOT advance before student answer has been validated and summary requested!
                return False

            # After tutor validates and asks about summary, any response advances to reflection
            return True

        # ============================================================
        # STEP 7: REFLECTION → END
        # AI asks for summary → student gives summary
        # ============================================================
        if self.current_step == ScaffoldStep.REFLECTION:
            if self.step_message_count < 1:
                return False
            if is_inquiring_or_confused():
                return self.step_message_count >= 4
            # Only advance if student gave substantive content (actual summary)
            if word_count >= 5:
                return True
            # Soft cap: after 3 AI messages in reflection, any response advances
            if self.step_message_count >= 3:
                return True
            return False

        return False

    def advance_step(self) -> None:
        """Advance to the next scaffold step or mark flow as complete."""
        steps = self.steps
        try:
            idx = steps.index(self.current_step)
        except ValueError:
            return

        if idx < len(steps) - 1:
            old_step = self.current_step
            self.current_step = steps[idx + 1]
            self.step_message_count = 0
            print(f"[FLOW] Advanced: {old_step.value} → {self.current_step.value}")
        else:
            if not self.completed:
                self.completed = True
                print("[FLOW] Session completed!")
