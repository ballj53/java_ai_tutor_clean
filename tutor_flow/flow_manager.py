# tutor_flow/flow_manager.py
"""
Manages the scaffolded tutoring flow.
SIMPLIFIED: Trust the AI to handle conversation flow within each step.
Advancement is based on simple rules, not complex state tracking.

"""

from __future__ import annotations
from typing import List
from .steps import ScaffoldStep, ConversationMessage, RoleType


class TutorFlow:
    """
    Manages the scaffolded tutoring flow.
    Simple state machine - AI handles the nuance within each step.
    """

    def __init__(self, topic_key: str) -> None:
        self.topic_key: str = topic_key
        self.current_step: ScaffoldStep = ScaffoldStep.INITIAL_METAPHOR
        self.messages: List[ConversationMessage] = []
        self.step_message_count: int = 0
        self.completed: bool = False

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

        We only advance when student clearly signals readiness.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())

        # Signals that student is ready to move on
        READY_SIGNALS = {
            "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "ready",
            "let's go", "go ahead", "next", "continue", "show me",
            "got it", "makes sense", "i understand", "understood",
            "i see", "that helps", "clear", "cool", "great", "nice",
            "sounds good", "alright", "perfect", "awesome"
        }

        # Signals that student needs more help (DON'T advance)
        NEEDS_HELP = {
            "confused", "confusing", "don't understand", "don't get it",
            "what do you mean", "can you explain", "help", "unclear",
            "lost", "wait", "hold on", "go back", "repeat", "again",
            "not sure", "i don't know", "huh", "what", "why", "how",
            "more", "example", "another"
        }

        def signals_ready() -> bool:
            # Check for ready signals, but not if they also signal confusion
            has_ready = any(signal in user_lower for signal in READY_SIGNALS)
            has_help = any(signal in user_lower for signal in NEEDS_HELP)
            return has_ready and not has_help

        def gave_substantive_answer() -> bool:
            # Student gave a real answer (not just "yes" or "ok")
            return word_count >= 6

        # ============================================================
        # STEP 1: INITIAL_METAPHOR → STUDENT_METAPHOR
        # Advance after AI gives opening metaphor and student responds
        # ============================================================

        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            # Advance after student gives their metaphor (at least 10 characters)
            # At least 5 characters OR 2+ words
            return len(user_message.strip()) > 5 or len(user_message.split()) >= 2  # AI spoke, any response advances

        # ============================================================
        # STEP 2: STUDENT_METAPHOR → VISUAL_DIAGRAM
        # Student shared metaphor, AI responded, student ready for visual
        # ============================================================
        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            if self.step_message_count < 1:
                return False
            return signals_ready()

        # ============================================================
        # STEP 3: VISUAL_DIAGRAM → CODE_STRUCTURE
        # Visual shown, student indicates understanding
        # ============================================================
        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            if self.step_message_count < 1:
                return False
            return signals_ready()

        # ============================================================
        # STEP 4: CODE_STRUCTURE → CODE_USAGE
        # AI shows code, student answers question OR says ready
        # Let AI handle validation within the step
        # ============================================================
        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            if self.step_message_count < 1:
                return False
            # Advance if: ready signal, OR gave substantive answer after code shown
            if signals_ready():
                return True
            if gave_substantive_answer():
                return True
            return False

        # ============================================================
        # STEP 5: CODE_USAGE → PRACTICE
        # Same pattern as above
        # ============================================================
        if self.current_step == ScaffoldStep.CODE_USAGE:
            if self.step_message_count < 1:
                return False
            if signals_ready():
                return True
            if gave_substantive_answer():
                return True
            return False

        # ============================================================
        # STEP 6: PRACTICE → REFLECTION
        # Must have: AI gives problem → student answers → AI validates → student ready
        # Don't advance on bare "yes" if problem hasn't been answered
        # ============================================================
        if self.current_step == ScaffoldStep.PRACTICE:
            if self.step_message_count < 2:
                # Need at least: problem given + validation
                # If student just says "yes" after 1 message, they're confirming
                # they want to practice, NOT that they're done practicing
                return False
            # After 2+ AI messages (problem + validation), ready signal advances
            return signals_ready()

        # ============================================================
        # STEP 7: REFLECTION → END
        # Must have: AI asks for summary → student gives summary
        # Don't advance on bare "yes" - need actual summary content
        # ============================================================
        if self.current_step == ScaffoldStep.REFLECTION:
            if self.step_message_count < 1:
                return False
            # Only advance if student gave substantive content (actual summary)
            # A bare "yes" should trigger AI to ask for summary
            if gave_substantive_answer():
                return True
            # After 2+ messages AND ready signal, also advance
            if self.step_message_count >= 2 and signals_ready():
                return True
            return False

        return False

    def advance_step(self) -> None:
        """Advance to the next scaffold step or mark flow as complete."""
        steps = list(ScaffoldStep)
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