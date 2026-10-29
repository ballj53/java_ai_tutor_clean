"""
Generates prompts for each scaffold step.
SIMPLIFIED: Give AI clear context and goals, trust it to execute well.
"""

from __future__ import annotations
import re
from typing import List, Optional
from .steps import (
    ScaffoldStep,
    ConversationMessage,
    is_student_question,
    has_help_signal,
    has_ready_signal,
    is_advance_request,
    is_bare_affirmative,
)


class StepGuide:
    """
    Generates AI prompts for each scaffold step.
    Focus: Clear goals + context. Let AI handle the conversation naturally.
    """

    @staticmethod
    def get_metaphor_prompt(topic) -> str:
        """Generate the initial metaphor prompt."""
        return (
            f"You are starting a tutoring session on {topic.name}.\n\n"
            f"CONCEPT: {topic.concept}\n\n"
            f"METAPHOR TO USE:\n{topic.metaphor_prompt}\n\n"
            "YOUR TASK:\n"
            "1. Introduce yourself briefly\n"
            "2. Explain the concept using the metaphor above\n"
            "3. End by asking: 'What does this remind you of from your own experience?'\n\n"
            "Keep it warm and under 150 words."
        )

    @staticmethod
    def get_response_prompt(
        topic,
        current_step: ScaffoldStep,
        user_input: str,
        context_messages: Optional[List[ConversationMessage]] = None,
        condition: int = 1,
    ) -> str:
        """
        Generate a prompt based on current step and conversation context.

        The AI should:
        - Respond naturally to what the student said
        - Accomplish the goal for this step
        - Transition smoothly to the next topic when appropriate
        """

        # Get topic-specific guidance if available
        topic_guidance = ""
        if hasattr(topic, "instructions_for"):
            topic_guidance = topic.instructions_for(current_step.value)
        elif hasattr(topic, "get_step_guidance"):
            topic_guidance = topic.get_step_guidance(current_step.value)

        # Build context from recent messages
        recent_context = ""
        if context_messages:
            recent_context = "RECENT CONVERSATION:\n"
            for msg in context_messages[-3:]:
                role = "Student" if msg.role == "user" else "You"
                recent_context += f"{role}: {msg.content[:250]}...\n"

        # Check whether code or usage examples have already been shown
        has_shown_code = any(
            m.role == "assistant"
            and (m.step == ScaffoldStep.CODE_STRUCTURE or getattr(m.step, "value", m.step) == ScaffoldStep.CODE_STRUCTURE.value)
            for m in (context_messages or [])
        )
        has_shown_usage = any(
            m.role == "assistant"
            and (m.step == ScaffoldStep.CODE_USAGE or getattr(m.step, "value", m.step) == ScaffoldStep.CODE_USAGE.value)
            for m in (context_messages or [])
        )
        has_shown_worked_example = any(
            m.role == "assistant"
            and (m.step == ScaffoldStep.WORKED_EXAMPLE or getattr(m.step, "value", m.step) == ScaffoldStep.WORKED_EXAMPLE.value)
            for m in (context_messages or [])
        )
        has_shown_guided_problem = any(
            m.role == "assistant"
            and (m.step == ScaffoldStep.GUIDED_PROBLEM or getattr(m.step, "value", m.step) == ScaffoldStep.GUIDED_PROBLEM.value)
            for m in (context_messages or [])
        )

        # ============================================================
        # STEP-SPECIFIC PROMPTS
        # ============================================================

        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "Respond to what they said and continue explaining the metaphor.\n"
                "End by asking what this reminds them of from their experience.\n"
                "Keep under 100 words."
            )

        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "WHAT TO DO:\n"
                "- If student shared a metaphor/example earlier and now says 'sure', 'yes', 'ready': "
                "They're ready for the visual! Say: 'Great! Let me show you a visual...'\n"
                "- If student just shared a new metaphor/example: Acknowledge it warmly, connect to the concept, "
                f"then introduce the crisis: \"{topic.agent_crisis}\" and ask 'Ready to see how this works visually?'\n\n"
                "Keep under 100 words."
            )

        if current_step == ScaffoldStep.VISUAL_DIAGRAM:
            return (
                f"TOPIC: {topic.name}\n\n"
                "A visual diagram was just shown to the student.\n"
                f"Student said: \"{user_input}\"\n\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR RESPONSE:\n"
                "- If they answered what part was helpful or understand: Acknowledge warmly and transition to code by saying: 'Now let's look at the actual code...'\n"
                "- DO NOT repeat the question 'What part of this diagram is most helpful?' if they already answered it.\n"
                "- If they asked a question or seem confused: Answer their question clearly in 1-2 sentences.\n\n"
                "Keep under 75 words."
            )

        if current_step == ScaffoldStep.CODE_STRUCTURE:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                f"CODE FOCUS: {topic.code_focus}\n\n"
                "YOUR TASK:\n"
                + (
                    "- Show the INTERNAL implementation code, highlight the key parts, and ask the question from TOPIC GUIDANCE.\n"
                    if not has_shown_code else
                    "- DO NOT show or repeat the implementation code again (it has already been shown).\n"
                    "- DO NOT repeat the question verbatim.\n"
                    "- If student answered or attempted your question: Validate their answer (RIGHT/WRONG), explain briefly, then ask 'Ready to see how to use this?'\n"
                    "- If student just asks to advance or says ready without answering: Remind them warmly: 'Before we move on, give the question a shot! [Prompt question briefly in 1 sentence]. What do you think?'\n"
                    "- If student asked a question or is confused: Answer their question directly and warmly in 1-2 sentences, then encourage them to answer.\n"
                )
                + "Keep under 150 words."
            )

        if current_step == ScaffoldStep.CODE_USAGE:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR TASK:\n"
                + (
                    "- Show simple USAGE examples, explain how it works from the user's perspective, and ask the question from TOPIC GUIDANCE.\n"
                    if not has_shown_usage else
                    "- DO NOT show or repeat the usage code again (it has already been shown).\n"
                    "- DO NOT repeat the question verbatim.\n"
                    "- If student answered your question: Validate their answer, then ask 'Ready to keep going?'\n"
                    "- If student just asks to advance or says ready without answering: Remind them warmly: 'Before we move on, give the question a shot! [Prompt question briefly in 1 sentence]. What do you think?'\n"
                    "- If student asked a question or is confused: Answer their question directly and warmly in 1-2 sentences, then encourage them to answer.\n"
                    "- If student says ready to move on / keep going (after you asked them): Confirm and prepare to move on.\n"
                )
                + "Keep under 120 words."
            )

        if current_step == ScaffoldStep.WORKED_EXAMPLE:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR TASK:\n"
                + (
                    "- Start with an encouraging transition easing the student in (e.g., 'To help you get comfortable with this, let's walk through a concrete example together step-by-step:').\n"
                    "- Present the WORKED EXAMPLE from TOPIC GUIDANCE clearly with the code and concise explanation.\n"
                    "- Ask the comprehension check question from TOPIC GUIDANCE.\n"
                    "- DO NOT invent your own problem or complex tasks. Stick strictly to the TOPIC GUIDANCE above.\n"
                    if not has_shown_worked_example else
                    "- DO NOT repeat the entire worked example code.\n"
                    "- Validate the student's response to your check question (RIGHT/WRONG with a brief explanation).\n"
                    "- If they understand or answered correctly, ask: 'Ready to try a simple guided problem to check your understanding?'\n"
                    "- If they asked a question or seem confused, answer in 1-2 friendly sentences and guide them.\n"
                )
                + "Keep under 140 words."
            )

        if current_step == ScaffoldStep.GUIDED_PROBLEM:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR TASK:\n"
                + (
                    "- Start with an encouraging transition (e.g., 'Great! Now let's try a guided problem together:').\n"
                    "- Present the GUIDED PROBLEM from TOPIC GUIDANCE clearly with the code and prompt.\n"
                    "- Ask the guided question from TOPIC GUIDANCE.\n"
                    "- DO NOT invent a complicated coding implementation task or ask for full code from scratch. Use ONLY the guided problem from TOPIC GUIDANCE.\n"
                    if not has_shown_guided_problem else
                    "- DO NOT repeat the full problem statement verbatim.\n"
                    "- Validate the student's solution or attempt explicitly.\n"
                    "- If correct (or close), explain briefly why it works and ask: 'You've got the hang of this! Ready to tackle a practice problem on your own?'\n"
                    "- DO NOT invent a new problem, challenge, or ask the student to write code. Only validate their answer and ask if they are ready for the practice problem.\n"
                    "- If incorrect, give a friendly hint without giving the full answer away.\n"
                )
                + "Keep under 130 words."
            )

        if current_step == ScaffoldStep.PRACTICE:
            tutor_practice_count = sum(
                1 for m in (context_messages or [])
                if m.role == "assistant" and (m.step == ScaffoldStep.PRACTICE or getattr(m.step, "value", m.step) == ScaffoldStep.PRACTICE.value)
            )

            if tutor_practice_count == 0:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student said: \"{user_input}\"\n\n"
                    "YOU MUST NOW INTRODUCE AND PRESENT THE PRACTICE PROBLEM.\n\n"
                    f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                    "MANDATORY FORMAT:\n"
                    "1. Start by briefly acknowledging or validating what the student said, followed by an encouraging transition that explicitly introduces the practice problem "
                    "(e.g., \"Spot on! Now let's put this into practice with a quick scenario:\" or "
                    "\"Great job! You've got the hang of this. Here is a practice problem to test your understanding:\").\n"
                    "2. Present the practice question from TOPIC GUIDANCE above.\n\n"
                    "CRITICAL RULES:\n"
                    "- NEVER output the question alone. You MUST include the introductory transition first.\n"
                    "- DO NOT praise them for a summary.\n"
                    "- DO NOT say 'Ready to summarize' yet.\n"
                    "- DO NOT invent a complicated coding implementation task.\n"
                    "- Keep under 80 words."
                )

            # Tutor already gave the practice problem. Student is responding.
            cleaned_input = re.sub(r'^(smart_toy|face)\s*', '', user_input.strip(), flags=re.IGNORECASE).strip()
            word_count = len(cleaned_input.split())
            is_question = is_student_question(cleaned_input) and not any(cleaned_input.lower().strip().endswith(tag) for tag in ["right?", "correct?", "yeah?", "yes?"])
            is_adv_req = is_advance_request(cleaned_input)
            is_bare_aff = is_bare_affirmative(cleaned_input)
            has_help = has_help_signal(cleaned_input)

            # Friendly reveal if the student has had 4+ exchanges and is still struggling, asking questions, confused, or trying to skip
            if tutor_practice_count >= 4 and (is_adv_req or is_question or is_bare_aff or has_help or word_count < 4):
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student said: \"{cleaned_input}\"\n\n"
                    f"TOPIC GUIDANCE SOLUTION & QUESTION:\n{topic_guidance}\n\n"
                    "THE STUDENT HAS STRUGGLED WITH THE PRACTICE PROBLEM ACROSS MULTIPLE TURNS.\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Acknowledge what they said warmly.\n"
                    "2. Kindly reveal and explain the solution in 1-2 clear, encouraging sentences using the TOPIC GUIDANCE above.\n"
                    "3. End by asking: 'Does that make sense? Ready to summarize what you learned?'\n\n"
                    "Keep under 70 words."
                )

            if is_adv_req or is_bare_aff:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student said: \"{cleaned_input}\"\n\n"
                    f"TOPIC GUIDANCE QUESTION:\n{topic_guidance}\n\n"
                    "THE STUDENT JUST ASKED TO ADVANCE OR SAID READY, BUT HAS NOT ATTEMPTED THE PRACTICE PROBLEM YET.\n\n"
                    "INSTRUCTIONS:\n"
                    "1. DO NOT validate them as correct.\n"
                    "2. DO NOT give away the answer yet.\n"
                    "3. DO NOT say 'Ready to summarize' yet.\n"
                    "4. Warmly encourage them to try the practice problem: "
                    "'Before we move to the summary, give the practice problem a shot! [Prompt question from TOPIC GUIDANCE briefly in 1 sentence]. What do you think?'\n\n"
                    "Keep under 60 words."
                )

            # The student asked a clarifying question without attempting the answer yet
            if is_question:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student asked a clarifying question: \"{cleaned_input}\"\n\n"
                    f"TOPIC GUIDANCE QUESTION:\n{topic_guidance}\n\n"
                    "INSTRUCTIONS:\n"
                    "1. Answer their clarifying question directly and warmly in 1-2 sentences.\n"
                    "2. Encourage them to try answering the practice question: 'What do you think happens in this scenario?'\n"
                    "3. DO NOT give away the answer yet.\n"
                    "4. DO NOT say 'Ready to summarize' yet.\n\n"
                    "Keep under 65 words."
                )

            # The student attempted/answered the practice problem
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student answered your practice question: \"{cleaned_input}\"\n\n"
                "VALIDATE THEIR ANSWER:\n"
                "1. Say 'Spot on!' or 'Exactly!' (or gently clarify if mistaken).\n"
                "2. Briefly explain why in 1-2 sentences.\n"
                "3. Say: 'Ready to summarize what you learned?'\n\n"
                "DO NOT ask any more practice questions or scenarios.\n"
                "Keep under 75 words."
            )

        if current_step == ScaffoldStep.REFLECTION:
            word_count = len(user_input.split())
            is_just_affirmative = word_count <= 3
            is_asking_question = is_student_question(user_input) and not any(
                user_input.lower().strip().endswith(tag) for tag in ["right?", "correct?", "yeah?", "yes?"]
            )

            if is_asking_question:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student asked a question: \"{user_input}\"\n\n"
                    "Answer their question clearly in 1-2 sentences, then ask them:\n"
                    f"'In your own words, what did you learn about {topic.name} today?'\n\n"
                    "Keep under 60 words."
                )
            elif is_just_affirmative:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"STUDENT JUST SAID: \"{user_input}\" (this is just an affirmative, NOT a summary)\n\n"
                    "YOU MUST NOW ASK FOR THEIR SUMMARY.\n\n"
                    f"Say: 'In your own words, what did you learn about {topic.name} today?'\n\n"
                    "DO NOT say 'Great summary!' - they haven't given one yet.\n"
                    "DO NOT move to quiz yet.\n"
                    "JUST ASK THE QUESTION.\n"
                    "Keep under 50 words."
                )
            else:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student gave their summary: \"{user_input}\"\n\n"
                    "THIS IS THEIR SUMMARY. ACCEPT IT.\n\n"
                    "Say:\n"
                    "1. 'Excellent summary!' (or similar praise)\n"
                    "2. One specific thing they got right\n"
                    "3. 'You're ready for the quiz!'\n\n"
                    "DO NOT ask follow-up questions.\n"
                    "DO NOT ask them to expand.\n"
                    "THIS IS THE END OF THE LESSON.\n"
                    "Keep under 60 words."
                )

        # Fallback
        return (
            f"Continue teaching {topic.name}.\n"
            f"Student said: \"{user_input}\"\n\n"
            "Respond helpfully and keep the lesson moving forward."
        )

    # Alias for compatibility
    get_prompt = get_response_prompt
