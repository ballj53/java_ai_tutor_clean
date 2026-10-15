"""
Survey Questions
Post-session survey to gather qualitative feedback
"""

import streamlit as st
from typing import Dict


SURVEY_QUESTIONS = {
    'learning_helpfulness': {
        'text': 'This tool helped me understand {topic} better than traditional methods (lecture, textbook, etc.)',
        'type': 'likert_5',
        'options': [
            'Strongly Disagree',
            'Disagree',
            'Neutral',
            'Agree',
            'Strongly Agree'
        ]
    },
    
    'vs_other_ai': {
        'text': 'This tool was more helpful than using ChatGPT or other AI chat tools directly',
        'type': 'likert_5',
        'options': [
            'Strongly Disagree',
            'Disagree',
            'Neutral',
            'Agree',
            'Strongly Agree'
        ]
    },
    
    'engagement': {
        'text': 'I felt engaged during the learning session',
        'type': 'likert_5',
        'options': [
            'Strongly Disagree',
            'Disagree',
            'Neutral',
            'Agree',
            'Strongly Agree'
        ]
    },
    
    'understanding': {
        'text': 'I feel confident I could explain {topic} to someone else',
        'type': 'likert_5',
        'options': [
            'Strongly Disagree',
            'Disagree',
            'Neutral',
            'Agree',
            'Strongly Agree'
        ]
    },
    
    'what_liked': {
        'text': 'What did you like most about this learning experience?',
        'type': 'text',
        'placeholder': 'Share your thoughts...'
    },
    
    # 'what_improve': {
    #     'text': 'What could be improved?',
    #     'type': 'text',
    #     'placeholder': 'Your suggestions...'
    # },
    
    'would_use_again': {
        'text': 'Would you use this tool again for other CS topics?',
        'type': 'yes_no',
        'options': ['Yes', 'No', 'Maybe']
    }
}




def render_survey(topic_name: str, condition: int) -> Dict:
    """
    Render the survey and return responses.
    
    Args:
        topic_name: Name of the topic (for substitution in questions)
        condition: 1 (character), 2 (non-character), or 3 (control)
    
    Returns:
        Dict of responses
    """
    st.header("📋 Quick Survey")
    st.write(f"Please share your thoughts about learning {topic_name}")
    st.write("This will help us improve the learning experience!")
    st.write("---")
    
    responses = {}
    
    # Render standard questions
    for key, q_data in SURVEY_QUESTIONS.items():
        q_text = q_data['text'].format(topic=topic_name)
        
        if q_data['type'] == 'likert_5':
            response = st.radio(
                q_text,
                options=q_data['options'],
                key=f"survey_{key}",
                index=None
            )
            responses[key] = response
            st.write("")  # Spacing
            
        elif q_data['type'] == 'text':
            response = st.text_area(
                q_text,
                placeholder=q_data.get('placeholder', ''),
                key=f"survey_{key}"
            )
            responses[key] = response
            st.write("")
            
        elif q_data['type'] == 'yes_no':
            response = st.radio(
                q_text,
                options=q_data['options'],
                key=f"survey_{key}",
                index=None
            )
            responses[key] = response
            st.write("")

    return responses


def validate_survey_complete(responses: Dict) -> tuple:
    """
    Check if all required questions are answered.
    
    Returns:
        (is_complete: bool, missing_count: int)
    """
    required_keys = list(SURVEY_QUESTIONS.keys())
    
    answered = 0
    for key in required_keys:
        if key in responses and responses[key]:
            answered += 1
    
    missing = len(required_keys) - answered
    is_complete = missing == 0
    
    return is_complete, missing


def get_survey_summary(responses: Dict) -> str:
    """Create a summary string of survey responses for export."""
    summary_parts = []
    
    for key, value in responses.items():
        if value:
            summary_parts.append(f"{key}={value}")
    
    return " | ".join(summary_parts)
