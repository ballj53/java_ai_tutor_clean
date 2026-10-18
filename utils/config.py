"""
Research Study Configuration
Core settings for the Java learning research study
"""

# Session Configuration
SESSION_DURATION = 15 * 60  # 10 minutes for learning
QUIZ_TIME_ESTIMATE = 10 * 60  # ~5 minutes for quiz (no hard limit)
SURVEY_TIME_ESTIMATE = 5 * 60  # ~3 minutes for survey

# Session Available Dates
SESSION_1_START = '2026-10-14'
SESSION_2_START = '2026-10-28'
SESSION_3_START = '2026-11-04'


# Study Configuration
TOTAL_PARTICIPANTS = 27
PARTICIPANTS_PER_CONDITION = 13

# Conditions
CONDITIONS = {
    1: "no_adaptive_scaffold", # Adaptive scaffold control group
    2: "adaptive_scaffold"     # Adaptive scaffold study group
}

# Manual condition assignments (override random assignment)
# Format: {'user_id': condition_number}
# Leave empty dict for fully random assignment
MANUAL_CONDITION_ASSIGNMENTS = {}



# Session Sequence
SESSIONS = {
    'session_1': {
        'id': 'arraylist',
        'name': 'Dynamic ArrayList',
        'start_date': SESSION_1_START,
        'topic_key': 'arraylist',
        'difficulty': 'easy',
        'order': 1,
        'description': 'Learn about dynamically sizing ArrayLists in Java'
    },
    'session_2': {
        'id': 'recursion',
        'name': 'Recursion',
        'start_date': SESSION_2_START,
        'topic_key': 'recursion',
        'difficulty': 'hard',
        'order': 2,
        'description': 'Learn about recursive functions in Java',
        'requires_completion': 'session_1'  # Must complete ArrayList first
    },
    'session_3': {
            'id': 'queue',
            'name': 'Queue',
            'start_date': SESSION_3_START,
            'topic_key': 'queue',
            'difficulty': 'medium',
            'order': 3,
            'description': 'Learn about queues and priority queues in Java',
            'requires_completion': 'session_1'  # Must complete ArrayList first (Recursion optional)
        }
}

# Data Collection
COLLECT_DATA = {
    'messages': True,           # All conversation messages
    'timestamps': True,         # Timestamp every interaction
    'scaffold_progress': True,  # Step progression
    'quiz_responses': True,     # Quiz answers
    'survey_responses': True,   # Survey answers
    'session_duration': True,   # Time spent
    'interaction_count': True   # Number of messages
}

# Export Settings
EXPORT_FORMAT = 'csv'
EXPORT_INCLUDE = [
    'user_id',
    'email',
    'condition',
    'section',
    'scaffold_tier',
    'topic',
    'session_start',
    'session_end',
    'duration_minutes',
    'message_count',
    'user_message_count',
    'assistant_message_count',
    'scaffold_steps_completed',
    'quiz_score',
    'quiz_total',
    'survey_responses',
    'completed'
]

# UI Settings
SHOW_DEBUG_INFO = False  # Set to True for testing, False for production
SHOW_SKIP_BUTTONS = True  # Set to True to enable "Skip to Quiz" button
REQUIRE_EMAIL_VERIFICATION = False  # Set to True if using email verification
ALLOW_MULTIPLE_ATTEMPTS = False  # Students can only do each session once

# Study Information (shown to students)
STUDY_INFO = {
    'title': 'Java Learning Research Study',
    'description': 'Help us understand how different teaching methods affect learning!',
    'institution': 'College of Charleston',
    'estimated_time': '~18 minutes per session (3 sessions total)',
    'contact': 'balljc1@g.cofc.edu'
}