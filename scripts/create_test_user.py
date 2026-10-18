"""
Create a Single Test User for Java AI Tutor

Usage:
    python scripts/create_test_user.py [email] [password] [condition] [section]

Examples:
    python scripts/create_test_user.py
    python scripts/create_test_user.py test@cofc.edu Password123! 1
    python scripts/create_test_user.py student2@cofc.edu MyPass456! 2 1
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_admin import auth as admin_auth, db
import utils.auth  # Initializes Firebase Admin SDK
from utils.config import CONDITIONS


def create_or_update_user(email: str, password: str, condition: int = 1, section: int = None):
    condition = int(condition)
    condition_name = CONDITIONS.get(condition, f"condition_{condition}")

    # 1. Create or get user in Firebase Authentication
    try:
        user = admin_auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )
        print(f"✅ Created user in Firebase Auth: {email} (UID: {user.uid})")
    except admin_auth.EmailAlreadyExistsError:
        user = admin_auth.get_user_by_email(email)
        admin_auth.update_user(user.uid, password=password)
        print(f"ℹ️  User {email} already exists in Auth (UID: {user.uid}). Password updated.")

    # 2. Setup user profile in Firebase Realtime Database
    user_ref = db.reference(f'users/{user.uid}')
    user_data = {
        'email': email,
        'condition': condition,
        'condition_name': condition_name,
        'assigned_date': time.time(),
        'sessions': {
            'arraylist': {'status': 'not_started'},
            'recursion': {'status': 'not_started'},
            'queue': {'status': 'not_started'}
        }
    }
    if section is not None:
        user_data['section'] = int(section)
    user_ref.set(user_data)

    print(f"✅ Realtime Database initialized at /users/{user.uid}")
    print(f"   - Condition: {condition} ({condition_name})")
    if section is not None:
        print(f"   - Section:   {section}")
    print(f"   - Sessions: arraylist, recursion, queue ('not_started')")
    print("\n🎉 Test user is ready to log in:")
    print(f"   Email:     {email}")
    print(f"   Password:  {password}")
    print(f"   Condition: {condition} ({condition_name})")
    if section is not None:
        print(f"   Section:   {section}\n")
    else:
        print()


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "test@cofc.edu"
    password = sys.argv[2] if len(sys.argv) > 2 else "Password123!"
    condition = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    section = int(sys.argv[4]) if len(sys.argv) > 4 else None

    create_or_update_user(email, password, condition, section)

