"""
Database Operations
Handle all data storage and retrieval for the research study
"""

import time
from firebase_admin import db
import streamlit as st
from typing import Optional, Dict, List


def save_session_start(user_id: str, session_id: str, condition: int):
    """Record that a session has started."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'status': 'in_progress',
            'start_time': time.time(),
            'condition': condition,
            'messages': [],
            'scaffold_progress': []
        })
    except Exception as e:
        st.error(f"Error saving session start: {e}")


def save_message(user_id: str, session_id: str, role: str, content: str, 
                 step: Optional[str] = None):
    """Save a conversation message."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}/messages')
        
        message_data = {
            'role': role,
            'content': content,
            'timestamp': time.time()
        }
        
        if step:
            message_data['step'] = step
        
        # Get current messages
        messages = ref.get() or []
        messages.append(message_data)
        
        # Save back
        ref.set(messages)
        
    except Exception as e:
        st.error(f"Error saving message: {e}")


def save_scaffold_progress(user_id: str, session_id: str, step: str):
    """Record scaffold step progression."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}/scaffold_progress')
        
        progress_data = {
            'step': step,
            'timestamp': time.time()
        }
        
        # Get current progress
        progress = ref.get() or []
        progress.append(progress_data)
        
        # Save back
        ref.set(progress)
        
    except Exception as e:
        st.error(f"Error saving scaffold progress: {e}")


def save_quiz_responses(user_id: str, session_id: str, responses: Dict, score: int, total: int):
    """Save quiz responses and score."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'quiz_responses': responses,
            'quiz_score': score,
            'quiz_total': total,
            'quiz_completed_time': time.time()
        })
    except Exception as e:
        st.error(f"Error saving quiz responses: {e}")


def save_survey_responses(user_id: str, session_id: str, responses: Dict):
    """Save survey responses."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        ref.update({
            'survey_responses': responses,
            'survey_completed_time': time.time()
        })
    except Exception as e:
        st.error(f"Error saving survey responses: {e}")


def complete_session(user_id: str, session_id: str):
    """Mark a session as complete."""
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        
        # Get session data
        session_data = ref.get()
        
        if session_data:
            start_time = session_data.get('start_time', time.time())
            duration = time.time() - start_time
            
            # Count messages
            messages = session_data.get('messages', [])
            user_messages = sum(1 for m in messages if m['role'] == 'user')
            assistant_messages = sum(1 for m in messages if m['role'] == 'assistant')
            
            ref.update({
                'status': 'completed',
                'end_time': time.time(),
                'duration_seconds': duration,
                'total_messages': len(messages),
                'user_messages': user_messages,
                'assistant_messages': assistant_messages
            })
    except Exception as e:
        st.error(f"Error completing session: {e}")


def get_session_status(user_id: str, session_id: str) -> str:
    """
    Get the status of a session.
    
    Returns: 'not_started', 'in_progress', 'completed'
    """
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')
        session_data = ref.get()
        
        if not session_data:
            return 'not_started'
        
        return session_data.get('status', 'not_started')
        
    except Exception as e:
        st.error(f"Error getting session status: {e}")
        return 'not_started'


def assign_adaptive_scaffold_tier(user_id: str, session_id: str, results: List[Dict]) -> Optional[str]:
    """
    Assigns adaptive scaffold tier based on the percentage
    of total difficulty points achieved in the Lesson 1 quiz:
    High Scaffold (Extra Support): <= 45%
    Regular Scaffold (Standard 7-Step Support): <= 75%
    Low Scaffold (Minimal Support): > 75%
    """

    try:
        # Fetch user data
        ref_user = db.reference(f'users/{user_id}')
        user_data = ref_user.get() or {}

        condition = user_data.get('condition', 1)

        # Calculate a weighted percentage score based on question difficulty
        total_possible = sum(r.get('difficulty', 1) for r in results)
        earned_points = sum(r.get('difficulty', 1) for r in results if r.get('is_correct'))
        weighted_pct = round((earned_points / total_possible * 100), 1) if total_possible > 0 else 0

        # Assign adaptive scaffold tiers based on weighted percentage
        if weighted_pct <= 45.0:
            tier = 'high'
        elif weighted_pct <= 75.0:
            tier = 'regular'
        else:
            tier = 'low'

        # Save the calculated tier information to the database
        ref_user.update({
            'scaffold_tier': tier,
            'binning_weighted_score': earned_points,
            'binning_weighted_total': total_possible,
            'binning_weighted_percentage': weighted_pct,
            'binning_timestamp': time.time(),
            'binning_source': session_id
        })

        print(f"[BINNING] User {user_id} binned into tier {tier}: {earned_points}/{total_possible} pts, {weighted_pct}%")
        return tier

    except Exception as e:
        st.error(f"Error assigning adaptive scaffold tier: {e}")
        return None


def get_user_scaffold_tier(user_id: str, session_id: Optional[str]) -> str:
    if session_id == 'arraylist':
        return 'regular'
    try:
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get() or {}
        return user_data.get('scaffold_tier', 'regular')
    except Exception as e:
        st.error(f"Error getting user scaffold tier: {e}")
        return 'regular'


def get_next_session(user_id: str) -> Optional[str]:
    """
    Determine which session the user should do next.
    
    Dynamically reads from SESSIONS config so new topics
    are picked up automatically.

    Returns: session id (e.g. 'arraylist', 'recursion', 'queue') or None if all complete
    """
    from utils.config import SESSIONS

    try:
        # Sort sessions by their 'order' field
        sorted_sessions = sorted(
            SESSIONS.values(),
            key=lambda s: s['order']
        )

        for session_config in sorted_sessions:
            session_id = session_config['id']
            status = get_session_status(user_id, session_id)

            if status != 'completed':
                return session_id

        # All sessions complete
        return None

    except Exception as e:
        st.error(f"Error getting next session: {e}")
        return None


def get_all_users() -> Dict:
    """Get all user data (admin only)."""
    try:
        ref = db.reference('users')
        return ref.get() or {}
    except Exception as e:
        st.error(f"Error getting all users: {e}")
        return {}


def get_user_condition(user_id: str) -> int:
    """Get the condition assigned to a user."""
    try:
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get()

        if user_data and 'condition' in user_data:
            return user_data['condition']

        # If no condition, something went wrong
        return 1

    except Exception as e:
        st.error(f"Error getting user condition: {e}")
        return 1


def export_data_to_dict() -> List[Dict]:
    """
    Export all data for analysis.

    Returns list of dicts, one per session completion.
    """
    try:
        all_users = get_all_users()
        export_data = []

        for user_id, user_data in all_users.items():
            email = user_data.get('email', '')
            condition = user_data.get('condition', 0)
            condition_name = user_data.get('condition_name', '')

            sessions = user_data.get('sessions', {})

            for session_id, session_data in sessions.items():
                if session_data.get('status') == 'completed':
                    messages = session_data.get('messages', [])

                    row = {
                        'user_id': user_id,
                        'email': email,
                        'condition': condition,
                        'condition_name': condition_name,
                        'topic': session_id,
                        'session_start': session_data.get('start_time', ''),
                        'session_end': session_data.get('end_time', ''),
                        'duration_seconds': session_data.get('duration_seconds', 0),
                        'duration_minutes': round(session_data.get('duration_seconds', 0) / 60, 2),
                        'total_messages': session_data.get('total_messages', 0),
                        'user_messages': session_data.get('user_messages', 0),
                        'assistant_messages': session_data.get('assistant_messages', 0),
                        'scaffold_steps_completed': len(session_data.get('scaffold_progress', [])),
                        'quiz_score': session_data.get('quiz_score', 0),
                        'quiz_total': session_data.get('quiz_total', 0),
                        'quiz_percentage': round((session_data.get('quiz_score', 0) / session_data.get('quiz_total', 1)) * 100, 1),
                        'survey_responses': str(session_data.get('survey_responses', {})),
                        'completed': True
                    }

                    export_data.append(row)

        return export_data

    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return []


def save_quiz_responses(user_id: str, session_id: str, responses: Dict,
                        score: int, total: int, results: List = None):
    """
    Save quiz responses, score, and difficulty breakdown.

    Args:
        user_id: User ID
        session_id: Session ID (arraylist or recursion)
        responses: Dict of question index -> user answer
        score: Number correct
        total: Total questions
        results: List of result dicts from score_quiz (includes difficulty)
    """
    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}')

        # Basic quiz data
        quiz_data = {
            'quiz_responses': responses,
            'quiz_score': score,
            'quiz_total': total,
            'quiz_percentage': round((score / total) * 100, 1) if total > 0 else 0,
            'quiz_completed_time': time.time()
        }

        # Add difficulty breakdown if results provided
        if results:
            difficulty_breakdown = calculate_difficulty_breakdown(results)
            quiz_data['difficulty_breakdown'] = difficulty_breakdown

            # Also save individual question details
            quiz_data['question_details'] = []
            for i, result in enumerate(results):
                quiz_data['question_details'].append({
                    'question_number': i,
                    'difficulty': result.get('difficulty', 0),
                    'is_correct': result.get('is_correct', False),
                    'user_answer': result.get('user_answer', ''),
                })

            if results and session_id == 'arraylist':
                assign_adaptive_scaffold_tier(user_id, session_id, results)

        ref.update(quiz_data)

    except Exception as e:
        st.error(f"Error saving quiz responses: {e}")


def calculate_difficulty_breakdown(results: List[Dict]) -> Dict:
    """
    Calculate performance by difficulty level.

    Returns:
        {
            'by_level': {
                1: {'correct': 2, 'total': 2, 'percentage': 100},
                2: {'correct': 1, 'total': 2, 'percentage': 50},
                ...
            },
            'average_difficulty_correct': 2.3,  # Avg difficulty of correct answers
            'average_difficulty_incorrect': 3.8  # Avg difficulty of incorrect answers
        }
    """
    breakdown = {
        'by_level': {},
        'average_difficulty_correct': 0,
        'average_difficulty_incorrect': 0
    }

    # Count by difficulty level
    difficulty_stats = {}
    correct_difficulties = []
    incorrect_difficulties = []

    for result in results:
        diff = result.get('difficulty', 0)
        is_correct = result.get('is_correct', False)

        # Track by level
        if diff not in difficulty_stats:
            difficulty_stats[diff] = {'correct': 0, 'total': 0}

        difficulty_stats[diff]['total'] += 1
        if is_correct:
            difficulty_stats[diff]['correct'] += 1
            correct_difficulties.append(diff)
        else:
            incorrect_difficulties.append(diff)

    # Convert to percentages
    for level, stats in difficulty_stats.items():
        breakdown['by_level'][level] = {
            'correct': stats['correct'],
            'total': stats['total'],
            'percentage': round((stats['correct'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0
        }

    # Calculate averages
    if correct_difficulties:
        breakdown['average_difficulty_correct'] = round(sum(correct_difficulties) / len(correct_difficulties), 2)

    if incorrect_difficulties:
        breakdown['average_difficulty_incorrect'] = round(sum(incorrect_difficulties) / len(incorrect_difficulties), 2)

    return breakdown


# ============================================================================
# QUERY FUNCTIONS FOR DIFFICULTY ANALYSIS
# ============================================================================

def get_difficulty_stats_by_condition(topic: str, difficulty_level: int) -> Dict:
    """
    Query: How many students answered a specific difficulty level correctly, by condition?

    Args:
        topic: 'arraylist' or 'recursion'
        difficulty_level: 1-5

    Returns:
        {
            'condition_1': {'correct': 15, 'total': 20, 'percentage': 75},
            'condition_2': {'correct': 12, 'total': 20, 'percentage': 60},
            'condition_3': {'correct': 10, 'total': 20, 'percentage': 50}
        }
    """
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}

        stats = {
            'condition_1': {'correct': 0, 'total': 0},
            'condition_2': {'correct': 0, 'total': 0},
            'condition_3': {'correct': 0, 'total': 0}
        }

        for user_id, user_data in all_users.items():
            condition = user_data.get('condition', 0)
            if condition not in [1, 2, 3]:
                continue

            session_data = user_data.get('sessions', {}).get(topic, {})
            question_details = session_data.get('question_details', [])

            for q in question_details:
                if q.get('difficulty') == difficulty_level:
                    stats[f'condition_{condition}']['total'] += 1
                    if q.get('is_correct'):
                        stats[f'condition_{condition}']['correct'] += 1

        # Add percentages
        for condition_key in stats:
            total = stats[condition_key]['total']
            if total > 0:
                stats[condition_key]['percentage'] = round(
                    (stats[condition_key]['correct'] / total) * 100, 1
                )
            else:
                stats[condition_key]['percentage'] = 0

        return stats

    except Exception as e:
        print(f"Error getting difficulty stats: {e}")
        return {}


def get_all_difficulty_stats(topic: str) -> Dict:
    """
    Get comprehensive difficulty statistics for a topic.

    Returns:
        {
            'by_difficulty': {
                1: {'condition_1': {...}, 'condition_2': {...}, 'condition_3': {...}},
                2: {...},
                ...
            },
            'overall': {
                'condition_1': {'avg_difficulty_correct': 2.3, 'avg_difficulty_incorrect': 3.8},
                'condition_2': {...},
                'condition_3': {...}
            }
        }
    """
    result = {
        'by_difficulty': {},
        'overall': {}
    }

    # Get stats for each difficulty level
    for difficulty in range(1, 6):  # 1-5
        result['by_difficulty'][difficulty] = get_difficulty_stats_by_condition(topic, difficulty)

    # Get overall averages
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}

        condition_avgs = {
            'condition_1': {'correct': [], 'incorrect': []},
            'condition_2': {'correct': [], 'incorrect': []},
            'condition_3': {'correct': [], 'incorrect': []}
        }

        for user_id, user_data in all_users.items():
            condition = user_data.get('condition', 0)
            if condition not in [1, 2, 3]:
                continue

            session_data = user_data.get('sessions', {}).get(topic, {})
            breakdown = session_data.get('difficulty_breakdown', {})

            avg_correct = breakdown.get('average_difficulty_correct', 0)
            avg_incorrect = breakdown.get('average_difficulty_incorrect', 0)

            if avg_correct > 0:
                condition_avgs[f'condition_{condition}']['correct'].append(avg_correct)
            if avg_incorrect > 0:
                condition_avgs[f'condition_{condition}']['incorrect'].append(avg_incorrect)

        # Calculate overall averages
        for condition_key, avgs in condition_avgs.items():
            result['overall'][condition_key] = {
                'avg_difficulty_correct': round(sum(avgs['correct']) / len(avgs['correct']), 2) if avgs[
                    'correct'] else 0,
                'avg_difficulty_incorrect': round(sum(avgs['incorrect']) / len(avgs['incorrect']), 2) if avgs[
                    'incorrect'] else 0,
                'n_students': len(avgs['correct'])
            }

    except Exception as e:
        print(f"Error calculating overall stats: {e}")

    return result


def export_difficulty_data_csv(topic: str, output_file: str = None):
    """
    Export difficulty data to CSV for analysis.

    Columns: user_id, email, condition, question_number, difficulty, is_correct, user_answer
    """
    import pandas as pd

    try:
        ref = db.reference('users')
        all_users = ref.get() or {}

        rows = []

        for user_id, user_data in all_users.items():
            email = user_data.get('email', '')
            condition = user_data.get('condition', 0)

            session_data = user_data.get('sessions', {}).get(topic, {})
            question_details = session_data.get('question_details', [])

            for q in question_details:
                rows.append({
                    'user_id': user_id,
                    'email': email,
                    'condition': condition,
                    'question_number': q.get('question_number', 0),
                    'difficulty': q.get('difficulty', 0),
                    'is_correct': q.get('is_correct', False),
                    'user_answer': q.get('user_answer', '')
                })

        df = pd.DataFrame(rows)

        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Exported to {output_file}")

        return df

    except Exception as e:
        print(f"Error exporting difficulty data: {e}")
        return None