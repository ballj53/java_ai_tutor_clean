"""
Bulk Firebase User Creation Script
Creates users from CSV/Excel file with email, password, and condition assignment
"""
import os
import re
import sys
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, db

# Initialize Firebase Admin SDK
def init_firebase():
    """Initialize Firebase - update path to your service account key"""
    try:
        path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
        cred = credentials.Certificate(path)
    except:
        # Alternative: use secrets dict
        import streamlit as st
        firebase_cfg = st.secrets["firebase"]
        service_account_info = {
            "type": firebase_cfg["type"],
            "project_id": firebase_cfg["project_id"],
            "private_key_id": firebase_cfg["private_key_id"],
            "private_key": firebase_cfg["private_key"],
            "client_email": firebase_cfg["client_email"],
            "client_id": firebase_cfg["client_id"],
            "auth_uri": firebase_cfg["auth_uri"],
            "token_uri": firebase_cfg["token_uri"],
            "auth_provider_x509_cert_url": firebase_cfg["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_cfg["client_x509_cert_url"],
        }
        cred = credentials.Certificate(service_account_info)
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_cfg["databaseURL"]  # Update this
    })


def extract_section_from_row(row, default_section=None):
    """Extract section from DataFrame row or return default_section"""
    for col in ['section', 'Section', 'section_number', 'Section_Number', 'section_num']:
        if col in row and pd.notna(row[col]):
            try:
                return int(row[col])
            except (ValueError, TypeError):
                return row[col]
    return default_section


def infer_section_from_filename(filename):
    """Try to infer section number from filename (e.g. section2_cleaned.csv -> 2)"""
    if isinstance(filename, str):
        match = re.search(r'section[_\s-]*(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def create_users_from_csv(csv_file, default_password="Cougars2026", section=None):
    """
    Create Firebase users from CSV file.
    
    CSV format:
    email,condition[,section]
    student1@cofc.edu,1,2
    student2@cofc.edu,2,2
    student3@cofc.edu,3,2
    """
    # Read CSV
    df = pd.read_csv(csv_file)
    default_section = section if section is not None else infer_section_from_filename(csv_file)
    return create_users_from_dataframe(df, default_password=default_password, default_section=default_section)


def create_users_from_excel(excel_file, sheet_name=0, default_password="JavaStudy2025", section=None):
    """
    Create Firebase users from Excel file.
    
    Excel format (Sheet 1):
    | email              | condition | section |
    |--------------------|-----------|---------|
    | student1@cofc.edu  | 1         | 2       |
    | student2@cofc.edu  | 2         | 2       |
    | student3@cofc.edu  | 3         | 2       |
    """
    # Read Excel
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    default_section = section if section is not None else infer_section_from_filename(excel_file)
    return create_users_from_dataframe(df, default_password=default_password, default_section=default_section)


def create_users_from_dataframe(df, default_password="Cougars2026", default_section=None):
    """Create users from pandas DataFrame"""
    
    results = {
        'created': [],
        'failed': [],
        'already_exist': []
    }
    
    for index, row in df.iterrows():
        email = row['email'].strip()
        condition = int(row['condition'])
        section = extract_section_from_row(row, default_section)
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=default_password,
                email_verified=False
            )
            
            section_msg = f", Section {section}" if section is not None else ""
            print(f"✅ Created: {email} → Condition {condition}{section_msg} (UID: {user.uid})")
            
            # Add to database with condition (and section)
            user_ref = db.reference(f'users/{user.uid}')
            user_data = {
                'email': email,
                'condition': condition,
                'condition_name': get_condition_name(condition),
                'assigned_date': pd.Timestamp.now().isoformat(),
                'sessions': {
                    'arraylist': {'status': 'not_started'},
                    'recursion': {'status': 'not_started'},
                    'queue': {'status': 'not_started'}
                }
            }
            if section is not None:
                user_data['section'] = section
            user_ref.set(user_data)
            
            created_entry = {
                'email': email,
                'uid': user.uid,
                'condition': condition,
                'password': default_password
            }
            if section is not None:
                created_entry['section'] = section
            results['created'].append(created_entry)
            
        except auth.EmailAlreadyExistsError:
            section_msg = f", Section {section}" if section is not None else ""
            print(f"⚠️  Already exists: {email} - Updating condition to {condition}{section_msg}")
            try:
                existing_user = auth.get_user_by_email(email)
                user_ref = db.reference(f'users/{existing_user.uid}')
                update_data = {
                    'condition': condition,
                    'condition_name': get_condition_name(condition)
                }
                if section is not None:
                    update_data['section'] = section
                user_ref.update(update_data)
                
                exist_entry = {
                    'email': email,
                    'condition': condition
                }
                if section is not None:
                    exist_entry['section'] = section
                results['already_exist'].append(exist_entry)
            except Exception as e:
                print(f"❌ Error updating {email}: {e}")
                results['failed'].append({'email': email, 'error': str(e)})
                
        except Exception as e:
            print(f"❌ Error creating {email}: {e}")
            results['failed'].append({'email': email, 'error': str(e)})
    
    return results


def get_condition_name(condition):
    """Get readable condition name"""
    conditions = {
        1: "no_adaptive_scaffold",
        2: "adaptive_scaffold"
    }
    return conditions.get(condition, "unknown")


def print_summary(results):
    """Print summary of user creation"""
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Created: {len(results['created'])} users")
    print(f"⚠️  Already existed: {len(results['already_exist'])} users")
    print(f"❌ Failed: {len(results['failed'])} users")
    print("="*60)
    
    if results['created']:
        print("\n📋 CREATED USERS:")
        for user in results['created']:
            section_info = f", Section: {user['section']}" if 'section' in user else ""
            print(f"  {user['email']} → Condition {user['condition']}{section_info} (Password: {user['password']})")
    
    if results['failed']:
        print("\n❌ FAILED:")
        for failure in results['failed']:
            print(f"  {failure['email']}: {failure['error']}")


def export_credentials(results, output_file='user_credentials.csv'):
    """Export created user credentials to CSV"""
    if results['created']:
        df = pd.DataFrame(results['created'])
        df.to_csv(output_file, index=False)
        print(f"\n💾 Credentials exported to: {output_file}")


def count_users_by_condition():
    """Count users by condition"""
    users = db.reference('users').get() or {}
    admins_emails = ["anissaewilliams@gmail.com", "anissawilliamschs@gmail.com",
                     "hashemin@cofc.edu", "rashidp@cofc.edu", "tiwaria@cofc.edu"]
    counts = {}

    for user in users.values():  # <-- iterate over values, not keys
        if user.get('email') not in admins_emails:
            condition = user.get('condition')
            if condition:
                counts[condition] = counts.get(condition, 0) + 1

    return counts


def count_users_by_section():
    """Count users by section"""
    users = db.reference('users').get() or {}
    admins_emails = ["anissaewilliams@gmail.com", "anissawilliamschs@gmail.com",
                     "hashemin@cofc.edu", "rashidp@cofc.edu", "tiwaria@cofc.edu"]
    counts = {}

    for user in users.values():
        if user.get('email') not in admins_emails:
            section = user.get('section')
            if section is not None:
                counts[section] = counts.get(section, 0) + 1

    return counts




# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def create_single_user(email, condition, password="Cougars2026", section=None):
    """Create a single user with given email, condition, and optional section"""
    try:
        # Create in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            email_verified=False
        )

        # Add to database
        user_ref = db.reference(f'users/{user.uid}')
        user_data = {
            'email': email,
            'condition': condition,
            'condition_name': get_condition_name(condition),
            'assigned_date': pd.Timestamp.now().isoformat(),
            'sessions': {
                'arraylist': {'status': 'not_started'},
                'recursion': {'status': 'not_started'},
                'queue': {'status': 'not_started'}
            }
        }
        if section is not None:
            user_data['section'] = int(section)
        user_ref.set(user_data)

        section_msg = f" → Section {section}" if section is not None else ""
        print(f"✅ Created: {email} → Condition {condition}{section_msg} (Password: {password})")
        return user.uid

    except auth.EmailAlreadyExistsError:
        print(f"⚠️  User already exists: {email}")
        try:
            existing_user = auth.get_user_by_email(email)
            user_ref = db.reference(f'users/{existing_user.uid}')
            update_data = {
                'condition': condition,
                'condition_name': get_condition_name(condition)
            }
            if section is not None:
                update_data['section'] = int(section)
            user_ref.update(update_data)
            return existing_user.uid
        except Exception as e:
            print(f"❌ Error updating {email}: {e}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    init_firebase()

    if len(sys.argv) >= 4:
        # Usage: python create_firebase_users.py email@example.com 1 2
        email = sys.argv[1]
        condition = int(sys.argv[2])
        section = int(sys.argv[3])
        create_single_user(email, condition, section=section)
    elif len(sys.argv) == 3:
        # Usage: python create_firebase_users.py email@example.com 1
        # OR: python create_firebase_users.py section2_cleaned.csv 2
        if sys.argv[1].endswith('.csv') or sys.argv[1].endswith('.xlsx'):
            file_path = sys.argv[1]
            section = int(sys.argv[2])
            if file_path.endswith('.csv'):
                results = create_users_from_csv(file_path, section=section)
            else:
                results = create_users_from_excel(file_path, section=section)
            print_summary(results)
        else:
            email = sys.argv[1]
            condition = int(sys.argv[2])
            create_single_user(email, condition)
    elif len(sys.argv) == 2 and (sys.argv[1].endswith('.csv') or sys.argv[1].endswith('.xlsx')):
        # Usage: python create_firebase_users.py section2_cleaned.csv
        file_path = sys.argv[1]
        if file_path.endswith('.csv'):
            results = create_users_from_csv(file_path)
        else:
            results = create_users_from_excel(file_path)
        print_summary(results)
    else:
        # Default: show counts
        print("User condition counts:")
        print(count_users_by_condition())
        print("User section counts:")
        print(count_users_by_section())


# if __name__ == "__main__":
#
#     # Initialize Firebase
#     init_firebase()
#     print("User condition counts")

#     print(count_users_by_condition())
#     # # OPTION 1: From CSV file
#     # #csv_file = sys.argv[1] if len(sys.argv) > 1 else 'test_user_load.csv'
#     # csv_file = 'section2_cleaned.csv'
#     # results = create_users_from_csv(csv_file, default_password='Cougars2026')
#     #
#     # # OPTION 2: From Excel file
#     # # results = create_users_from_excel('students.xlsx', default_password='JavaStudy2025')
#     #
#     # # Print summary
#     # print_summary(results)
#     #
#     # # Export credentials
#     # export_credentials(results, 'created_users_section_2.csv')
#
#     #print("\n✅ Done! Users can now login with their email and password: Cougars2026")
