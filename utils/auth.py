import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, auth as admin_auth, db
from utils.config import MANUAL_CONDITION_ASSIGNMENTS, CONDITIONS
import time

# ---------------------------------------------------------
# Firebase Initialization (Admin SDK)
# ---------------------------------------------------------

def init_firebase():
    """Initialize Firebase Admin SDK once."""
    if not firebase_admin._apps:
        # Extract only the service account fields
        firebase_cfg = st.secrets["firebase"]
        service_account_keys = {
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri",
            "auth_provider_x509_cert_url",
            "client_x509_cert_url",
        }

        service_account_info = {
            k: firebase_cfg[k] for k in service_account_keys if k in firebase_cfg
        }

        if "private_key" in service_account_info:
            service_account_info["private_key"] = (
                str(service_account_info["private_key"]).replace("\\n", "\n")
            )

        db_url = firebase_cfg.get("databaseURL")
        if not db_url and "project_id" in firebase_cfg:
            db_url = f"https://{firebase_cfg['project_id']}-default-rtdb.firebaseio.com"

        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, {
            "databaseURL": db_url
        })

init_firebase()


# ---------------------------------------------------------
# Firebase REST API Login (Email/Password)
# ---------------------------------------------------------

FIREBASE_API_KEY = st.secrets["firebase"]["apiKey"]

def firebase_login(email: str, password: str):
    """
    Authenticate a user using Firebase's REST API.
    Returns a dict containing idToken, refreshToken, localId, etc.
    Raises ValueError on failure.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        # After successful login, ensure user has condition assigned
        user_id = data["localId"]
        assign_condition_if_needed(user_id, email)
        return data
    else:
        error_msg = data.get("error", {}).get("message", "Login failed")
        raise ValueError(error_msg)


def assign_condition_if_needed(user_id: str, email: str):
    """
    Assign condition to user based on manual assignments.
    If email not in manual assignments, assign based on balanced distribution.
    """
    try:
        ref = db.reference(f'users/{user_id}')
        user_data = ref.get()
        
        # If user already has condition, don't change it
        if user_data and 'condition' in user_data:
            return
        
        # Check manual assignments first
        if email in MANUAL_CONDITION_ASSIGNMENTS:
            assigned_condition = MANUAL_CONDITION_ASSIGNMENTS[email]
        else:
            # Auto-assign based on balanced distribution
            assigned_condition = get_balanced_condition()
        
        # Create or update user record
        if not user_data:
            user_data = {
                'email': email,
                'condition': assigned_condition,
                'condition_name': CONDITIONS[assigned_condition],
                'assigned_date': time.time(),
                'sessions': {
                    'arraylist': {'status': 'not_started'},
                    'recursion': {'status': 'not_started'}
                }
            }
            ref.set(user_data)
        else:
            # User exists but no condition
            ref.update({
                'condition': assigned_condition,
                'condition_name': CONDITIONS[assigned_condition],
                'assigned_date': time.time()
            })
            
    except Exception as e:
        st.error(f"Error assigning condition: {e}")


def get_balanced_condition() -> int:
    """
    Assign condition based on balanced distribution (2 conditions only for regular vs. adaptive study).
    Returns the condition with fewest users.
    """
    try:
        ref = db.reference('users')
        all_users = ref.get() or {}
        
        condition_counts = {1: 0, 2: 0}
        for user_data in all_users.values():
            condition = user_data.get('condition', 0)
            if condition in condition_counts:
                condition_counts[condition] += 1
        
        # Return condition with fewest users
        return min(condition_counts, key=condition_counts.get)
        
    except Exception as e:
        st.error(f"Error getting balanced condition: {e}")
        return 1  # Default to condition 1


def get_user_data(user_id: str) -> dict:
    """Fetch user record from Firebase Realtime Database."""
    try:
        ref = db.reference(f'users/{user_id}')
        return ref.get() or {}
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return {}


# ---------------------------------------------------------
# Session Helpers
# ---------------------------------------------------------

def set_session(user_data: dict):
    """Store user login info in Streamlit session_state."""
    st.session_state["logged_in"] = True
    st.session_state["id_token"] = user_data["idToken"]
    st.session_state["refresh_token"] = user_data["refreshToken"]
    st.session_state["user_id"] = user_data["localId"]
    st.session_state["email"] = user_data.get("email")
    st.session_state["condition"] = user_data.get("condition")


def logout_user():
    """Clear session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
