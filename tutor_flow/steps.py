# tutor_flow/steps.py
"""
Scaffold steps and message types.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
import time
import re


class ScaffoldStep(Enum):
    """Stages of the pedagogical scaffold."""
    INITIAL_METAPHOR = "initial_metaphor"
    STUDENT_METAPHOR = "student_metaphor"
    VISUAL_DIAGRAM = "visual_diagram"
    CODE_STRUCTURE = "code_structure"
    CODE_USAGE = "code_usage"
    PRACTICE = "practice"
    REFLECTION = "reflection"


RoleType = Literal["user", "assistant", "system"]


@dataclass
class ConversationMessage:
    """Message exchanged during a scaffolded tutoring session."""
    role: RoleType
    content: str
    step: ScaffoldStep
    timestamp: float = field(default_factory=time.time)


# Generic signals for scaffold progression across all topics
READY_SIGNALS = {
    "yes", "yeah", "yep", "yup", "sure", "ok", "okay", "ready",
    "let's go", "go ahead", "next", "continue", "show me",
    "got it", "makes sense", "i understand", "understood",
    "i see", "that helps", "clear", "cool", "great", "nice",
    "sounds good", "alright", "perfect", "awesome"
}

NEEDS_HELP = {
    "confused", "confusing", "confusion",
    "don't understand", "dont understand", "do not understand",
    "don't get", "dont get", "do not get", "don't get it", "dont get it",
    "doesn't make sense", "doesnt make sense", "does not make sense",
    "what do you mean", "can you explain", "could you explain", "explain that",
    "help", "unclear", "lost", "i'm lost", "im lost",
    "wait", "hold on", "go back", "repeat", "repeat that",
    "not sure", "i don't know", "i dont know", "huh",
    "tell me more", "give me an example", "another example", "more examples",
    "i have a question", "can i ask", "quick question"
}


def is_student_question(text: str) -> bool:
    """Returns True if the student asked a question rather than answering."""
    t = text.strip().lower()
    return "?" in t


def has_help_signal(text: str) -> bool:
    """Returns True if the text contains any phrase signaling confusion or request for help."""
    t = text.strip().lower()
    return any(re.search(r"\b" + re.escape(sig) + r"\b", t) for sig in NEEDS_HELP)


def has_ready_signal(text: str) -> bool:
    """Returns True if the text contains any phrase signaling readiness to proceed."""
    t = text.strip().lower()
    return any(re.search(r"\b" + re.escape(sig) + r"\b", t) for sig in READY_SIGNALS)

ADVANCE_PATTERNS = [
    r"\bwhat(\'?s| is) next\b",
    r"\b(let\'?s|can we|shall we) (keep going|move on|continue|proceed|advance)\b",
    r"\bkeep going\b",
    r"\bmove on\b",
    r"\bnext step\b",
    r"\bready to (move on|continue|advance|keep going)\b",
    r"\bwhat do we do next\b",
]


def is_advance_request(text: str) -> bool:
    """Returns True if the student is merely asking to advance without answering."""
    t = text.strip().lower()
    return any(re.search(pat, t) for pat in ADVANCE_PATTERNS)


def is_bare_affirmative(text: str) -> bool:
    """Returns True if the student just gave a short ready/affirmative phrase."""
    words = text.strip().lower().split()
    return len(words) <= 2 and has_ready_signal(text)
