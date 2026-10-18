"""
Data Export Module
Export research data to CSV for analysis
"""

import csv
import io
from datetime import datetime
from utils.database import export_data_to_dict
import streamlit as st


def generate_csv() -> str:
    """
    Generate CSV string of all research data.
    
    Returns:
        CSV string ready for download
    """
    data = export_data_to_dict()
    
    if not data:
        return ""
    
    # Create CSV in memory
    output = io.StringIO()
    
    # Get all possible keys from all rows
    all_keys = set()
    for row in data:
        all_keys.update(row.keys())
    
    fieldnames = sorted(list(all_keys))
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue()


def generate_detailed_csv_with_messages() -> str:
    """
    Generate detailed CSV including message-level data.
    Each row is a message (for conversation analysis).
    """
    from utils.database import get_all_users
    
    users = get_all_users()
    output = io.StringIO()
    
    fieldnames = [
        'user_id', 'email', 'condition', 'condition_name', 'section',
        'topic', 'message_number', 'role', 'content', 
        'timestamp', 'step'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for user_id, user_data in users.items():
        email = user_data.get('email', '')
        condition = user_data.get('condition', 0)
        condition_name = user_data.get('condition_name', '')
        section = user_data.get('section', '')
        
        sessions = user_data.get('sessions', {})
        
        for topic, session_data in sessions.items():
            messages = session_data.get('messages', [])
            
            for i, msg in enumerate(messages):
                writer.writerow({
                    'user_id': user_id,
                    'email': email,
                    'condition': condition,
                    'condition_name': condition_name,
                    'section': section,
                    'topic': topic,
                    'message_number': i + 1,
                    'role': msg.get('role', ''),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', ''),
                    'step': msg.get('step', '')
                })
    
    return output.getvalue()


def render_admin_export():
    """Render admin export interface."""
    st.title("📊 Data Export (Admin)")
    
    st.write("Export research data for analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Summary Data")
        st.write("One row per completed session")
        
        if st.button("Generate Summary CSV"):
            csv_data = generate_csv()
            
            if csv_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"research_data_summary_{timestamp}.csv"
                
                st.download_button(
                    label="📥 Download Summary CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                
                # Show preview
                st.write("Preview (first 5 rows):")
                lines = csv_data.split('\n')
                st.code('\n'.join(lines[:6]))
            else:
                st.warning("No data available yet")
    
    with col2:
        st.subheader("Detailed Message Data")
        st.write("One row per message (for conversation analysis)")
        
        if st.button("Generate Detailed CSV"):
            csv_data = generate_detailed_csv_with_messages()
            
            if csv_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"research_data_detailed_{timestamp}.csv"
                
                st.download_button(
                    label="📥 Download Detailed CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv"
                )
                
                # Show preview
                st.write("Preview (first 5 rows):")
                lines = csv_data.split('\n')
                st.code('\n'.join(lines[:6]))
            else:
                st.warning("No data available yet")
    
    # Show statistics
    st.write("---")
    st.subheader("Study Statistics")
    
    from utils.database import get_all_users
    
    users = get_all_users()
    
    total_users = len(users)
    condition_counts = {1: 0, 2: 0, 3: 0}
    completed_arraylist = 0
    completed_recursion = 0
    completed_both = 0
    
    for user_data in users.values():
        condition = user_data.get('condition', 0)
        if condition in condition_counts:
            condition_counts[condition] += 1
        
        sessions = user_data.get('sessions', {})
        
        arraylist_complete = sessions.get('arraylist', {}).get('status') == 'completed'
        recursion_complete = sessions.get('recursion', {}).get('status') == 'completed'
        
        if arraylist_complete:
            completed_arraylist += 1
        if recursion_complete:
            completed_recursion += 1
        if arraylist_complete and recursion_complete:
            completed_both += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Participants", total_users)
        st.metric("Completed ArrayList", completed_arraylist)
    
    with col2:
        st.metric("Condition 1 (Character)", condition_counts[1])
        st.metric("Completed Recursion", completed_recursion)
    
    with col3:
        st.metric("Conditions 2 & 3", condition_counts[2] + condition_counts[3])
        st.metric("Completed Both", completed_both)
    
    # Completion rates
    st.write("---")
    st.subheader("Completion Rates by Condition")
    
    for condition in [1, 2, 3]:
        condition_users = [u for u in users.values() if u.get('condition') == condition]
        
        if condition_users:
            completed = sum(1 for u in condition_users 
                          if u.get('sessions', {}).get('arraylist', {}).get('status') == 'completed')
            rate = (completed / len(condition_users)) * 100
            
            condition_name = {1: "Character Scaffolded", 2: "Non-Character Scaffolded", 3: "Direct Chat"}[condition]
            st.write(f"**{condition_name}:** {completed}/{len(condition_users)} ({rate:.1f}%)")
