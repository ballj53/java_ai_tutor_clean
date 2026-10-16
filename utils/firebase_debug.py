"""
Firebase Data Verification & Debugging Tools
Use this to verify data is being saved correctly
"""

import streamlit as st
from firebase_admin import db
import json
from datetime import datetime


def verify_firebase_connection():
    """Test if Firebase is connected and working."""
    st.subheader("🔌 Firebase Connection Test")

    try:
        # Try to read from root
        ref = db.reference('/')
        data = ref.get()

        if data is not None:
            st.success("✅ Firebase connected successfully!")
            st.write(f"Database has {len(data) if isinstance(data, dict) else 0} top-level keys")
            return True
        else:
            st.success("✅ Firebase connected (empty database)")
            return True

    except Exception as e:
        st.error(f"❌ Firebase connection failed: {e}")
        return False


def view_user_data(user_id: str = None):
    """View all data for a specific user."""
    st.subheader("👤 User Data Viewer")

    if not user_id:
        user_id = st.text_input("Enter User ID to inspect:", key="user_id_input")

    if user_id:
        try:
            ref = db.reference(f'users/{user_id}')
            user_data = ref.get()

            if user_data:
                st.success(f"✅ User {user_id} found!")

                # Show user info
                st.write("**Email:**", user_data.get('email', 'N/A'))
                st.write("**Condition:**", user_data.get('condition', 'N/A'))
                st.write("**Condition Name:**", user_data.get('condition_name', 'N/A'))

                # Show sessions
                st.write("---")
                st.write("**Sessions:**")

                sessions = user_data.get('sessions', {})
                for session_id, session_data in sessions.items():
                    with st.expander(f"📚 {session_id} - {session_data.get('status', 'unknown')}"):
                        st.json(session_data)

                # Download full data
                st.download_button(
                    "📥 Download User Data (JSON)",
                    data=json.dumps(user_data, indent=2),
                    file_name=f"user_{user_id}.json",
                    mime="application/json"
                )
            else:
                st.warning(f"⚠️ User {user_id} not found in database")

        except Exception as e:
            st.error(f"Error viewing user data: {e}")


def view_all_users_summary():
    """Show summary of all users in the database."""
    st.subheader("👥 All Users Summary")

    try:
        ref = db.reference('users')
        all_users = ref.get() or {}

        if not all_users:
            st.warning("No users in database yet")
            return

        st.write(f"**Total Users:** {len(all_users)}")

        # Create summary table
        summary_data = []

        for user_id, user_data in all_users.items():
            email = user_data.get('email', 'N/A')
            condition = user_data.get('condition', 'N/A')

            sessions = user_data.get('sessions', {})
            arraylist_status = sessions.get('arraylist', {}).get('status', 'not_started')
            recursion_status = sessions.get('recursion', {}).get('status', 'not_started')

            summary_data.append({
                'User ID': user_id[:8] + '...',  # Shortened for display
                'Email': email,
                'Condition': condition,
                'ArrayList': arraylist_status,
                'Recursion': recursion_status
            })

        st.table(summary_data)

        # Show detailed data for selected user
        st.write("---")
        selected_email = st.selectbox(
            "Select user to view details:",
            options=[u.get('email', 'Unknown') for u in all_users.values()]
        )

        if selected_email:
            # Find user_id for this email
            for uid, udata in all_users.items():
                if udata.get('email') == selected_email:
                    view_user_data(uid)
                    break

    except Exception as e:
        st.error(f"Error viewing users: {e}")


def view_session_messages(user_id: str, session_id: str):
    """View all messages for a specific session."""
    st.subheader(f"💬 Messages: {session_id}")

    try:
        ref = db.reference(f'users/{user_id}/sessions/{session_id}/messages')
        messages = ref.get() or []

        if not messages:
            st.warning("No messages in this session yet")
            return

        st.write(f"**Total Messages:** {len(messages)}")

        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 0)
            step = msg.get('step', 'N/A')

            # Format timestamp
            dt = datetime.fromtimestamp(timestamp) if timestamp else None
            time_str = dt.strftime("%H:%M:%S") if dt else "N/A"

            # Display message
            with st.expander(f"{i + 1}. {role.upper()} ({time_str}) - Step: {step}"):
                st.write(content)

    except Exception as e:
        st.error(f"Error viewing messages: {e}")


def test_data_saving():
    """Interactive test to verify data saving works."""
    st.subheader("🧪 Test Data Saving")

    st.write("This will create a test entry in Firebase to verify saving works.")

    test_user_id = st.text_input("Test User ID:", value="test_user_123")
    test_email = st.text_input("Test Email:", value="test@test.com")

    if st.button("Create Test User"):
        try:
            ref = db.reference(f'users/{test_user_id}')
            ref.set({
                'email': test_email,
                'condition': 1,
                'condition_name': 'control_scaffolded',
                'test': True,
                'created_at': datetime.now().isoformat(),
                'sessions': {
                    'arraylist': {'status': 'not_started'},
                    'recursion': {'status': 'not_started'}
                }
            })

            st.success("✅ Test user created!")
            st.write("Now check if it appears in the database:")

            # Verify it was saved
            saved_data = ref.get()
            st.json(saved_data)

        except Exception as e:
            st.error(f"❌ Error creating test user: {e}")

    if st.button("Delete Test User"):
        try:
            ref = db.reference(f'users/{test_user_id}')
            ref.delete()
            st.success("✅ Test user deleted")
        except Exception as e:
            st.error(f"Error deleting test user: {e}")


def check_data_structure():
    """Verify the data structure matches what we expect."""
    st.subheader("🏗️ Data Structure Verification")

    try:
        ref = db.reference('users')
        all_users = ref.get() or {}

        if not all_users:
            st.info("No users yet - database structure cannot be verified")
            return

        # Pick first user to check structure
        first_user_id = list(all_users.keys())[0]
        first_user = all_users[first_user_id]

        st.write("**Expected Structure:**")
        expected = {
            'email': 'string',
            'condition': 'int (1, 2, or 3)',
            'condition_name': 'string',
            'assigned_date': 'timestamp',
            'sessions': {
                'arraylist': {
                    'status': 'string',
                    'start_time': 'timestamp (optional)',
                    'messages': 'list',
                    'scaffold_progress': 'list',
                    'quiz_responses': 'dict',
                    'survey_responses': 'dict'
                },
                'recursion': '...'
            }
        }
        st.json(expected)

        st.write("**Actual Structure (first user):**")
        st.json(first_user)

        # Check for required fields
        st.write("---")
        st.write("**Validation:**")

        checks = {
            'Has email': 'email' in first_user,
            'Has condition': 'condition' in first_user,
            'Has sessions': 'sessions' in first_user,
            'Has arraylist session': 'arraylist' in first_user.get('sessions', {}),
            'Has recursion session': 'recursion' in first_user.get('sessions', {}),
        }

        for check, passed in checks.items():
            if passed:
                st.success(f"✅ {check}")
            else:
                st.error(f"❌ {check}")

    except Exception as e:
        st.error(f"Error checking structure: {e}")


def render_debug_dashboard():
    """Main debugging dashboard."""
    st.title("🔍 Firebase Data Verification Dashboard")

    st.write("Use this dashboard to verify data is being saved correctly.")

    # Connection test
    with st.expander("🔌 Test Firebase Connection", expanded=True):
        verify_firebase_connection()

    # View all users
    with st.expander("👥 View All Users"):
        view_all_users_summary()

    # View specific user
    with st.expander("👤 View Specific User"):
        view_user_data()

    # Data structure check
    with st.expander("🏗️ Verify Data Structure"):
        check_data_structure()

    # Test data saving
    with st.expander("🧪 Test Data Saving"):
        test_data_saving()

    # Export current data
    with st.expander("📥 Export Current Data"):
        from data_export import generate_csv

        if st.button("Generate Current Data CSV"):
            csv_data = generate_csv()

            if csv_data:
                st.download_button(
                    "📥 Download CSV",
                    data=csv_data,
                    file_name=f"firebase_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

                # Show preview
                st.write("**Preview:**")
                lines = csv_data.split('\n')[:10]
                st.code('\n'.join(lines))
            else:
                st.info("No completed sessions yet")


# Add this to app_research.py to access the debug dashboard
def show_debug_if_requested():
    """Check if debug mode is requested via URL parameter."""
    if st.query_params.get("debug") == "true":
        render_debug_dashboard()
        return True
    return False