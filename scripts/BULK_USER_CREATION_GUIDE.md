# 🚀 Bulk Create Firebase Users - Quick Guide

## What This Does
Creates Firebase user accounts from a spreadsheet and automatically assigns conditions.

## Quick Setup

### 1. Prepare Your Spreadsheet

**CSV Format:**
```csv
email,condition,section
student1@cofc.edu,1,1
student2@cofc.edu,2,1
student3@cofc.edu,1,2
```
*(Note: `section` column is optional. You can also pass section via CLI or let it auto-detect from filenames like `section2_cleaned.csv`)*

**Excel Format:**
Same columns, any sheet name.

### 2. Update Firebase Config

Edit `create_firebase_users.py` line 47:
```python
'databaseURL': 'YOUR_DATABASE_URL'  # Replace with your Firebase URL
```

### 3. Run the Script

```bash
# Bulk creation from CSV:
python create_firebase_users.py section2_cleaned.csv

# Bulk creation with explicit section:
python create_firebase_users.py students.csv 2

# Single user creation:
python create_firebase_users.py student@cofc.edu 1 2

# View current user counts by condition and section:
python create_firebase_users.py
```

## What You Need

### Install Dependencies
```bash
pip install pandas firebase-admin openpyxl
```

### Firebase Service Account
Get from Firebase Console → Project Settings → Service Accounts → Generate New Private Key

Save as `.streamlit/secrets.toml` or separate JSON file.

## Usage Options

### Option 1: CSV File
```python
results = create_users_from_csv('section2_cleaned.csv', default_password='JavaStudy2025')
```

### Option 2: Excel File
```python
results = create_users_from_excel('students.xlsx', default_password='JavaStudy2025', section=2)
```

### Option 3: Custom Password
```python
results = create_users_from_csv('students.csv', default_password='YourPassword123', section=1)
```

## What Happens

For each row:
1. ✅ Creates user in Firebase Auth
2. ✅ Sets password to `JavaStudy2025` (or custom)
3. ✅ Adds to Realtime Database with:
   - Email
   - Condition (1 or 2)
   - Section (e.g. 1, 2, or 3)
   - Session status (arraylist, recursion, queue all not_started)
   - Assigned date

## Output

### Console Output
```
✅ Created: student1@cofc.edu → Condition 1, Section 1 (UID: abc123)
✅ Created: student2@cofc.edu → Condition 2, Section 1 (UID: def456)
⚠️  Already exists: student3@cofc.edu - Updating condition to 1, Section 2

===========================================================
SUMMARY
===========================================================
✅ Created: 58 users
⚠️  Already existed: 2 users
❌ Failed: 0 users
===========================================================
```

### Credentials File
Creates `user_credentials.csv`:
```csv
email,uid,condition,password,section
student1@cofc.edu,abc123,1,JavaStudy2025,1
student2@cofc.edu,def456,2,JavaStudy2025,1
```

## Give to Students

Send each student:
```
Login URL: https://your-app.streamlit.app
Email: [their email]
Password: JavaStudy2025
```

## Condition Distribution

**Balanced 60 students:**
- Condition 1 (Character + Scaffold): Students 1-20
- Condition 2 (No Character + Scaffold): Students 21-40  
- Condition 3 (Direct Chat): Students 41-60

## Troubleshooting

### "Email already exists"
Script will UPDATE the condition for existing users.

### "Permission denied"
Check Firebase service account has Admin SDK Admin Service Agent role.

### "Invalid credentials"
Verify your `secrets.toml` or service account JSON is correct.

## Quick Example

```python
# create_users.py
import firebase_admin
from firebase_admin import credentials, auth, db

# Initialize
cred = credentials.Certificate('service-account.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project.firebaseio.com'
})

# Create users
import pandas as pd
df = pd.read_csv('students.csv')

for _, row in df.iterrows():
    email = row['email']
    condition = row['condition']
    
    # Create user
    user = auth.create_user(
        email=email,
        password='JavaStudy2025'
    )
    
    # Add to database
    db.reference(f'users/{user.uid}').set({
        'email': email,
        'condition': condition,
        'condition_name': ['', 'character_scaffolded', 'non_character_scaffolded', 'direct_chat'][condition],
        'sessions': {
            'arraylist': {'status': 'not_started'},
            'recursion': {'status': 'not_started'}
        }
    })
    
    print(f"✅ {email} → Condition {condition}")
```

## Done! 🎉

Students can now login with:
- Email: [their email from spreadsheet]
- Password: JavaStudy2025
