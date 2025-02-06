import streamlit as st
import datetime
from services.google_calendar import GoogleCalendarService
from services.apple_calendar import AppleCalendarService
from services.task_manager import TaskManager
from visualization.progress_charts import create_progress_chart, create_trend_chart
from utils.deduplication import deduplicate_events
from models.database import get_db

# Initialize database
next(get_db())

def initialize_session_state():
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.date.today()

def main():
    st.title("Calendar & Task Tracker")
    
    initialize_session_state()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Calendar View", "Task Management", "Progress Analytics"]
    )
    
    if page == "Calendar View":
        display_calendar_view()
    elif page == "Task Management":
        display_task_management()
    else:
        display_progress_analytics()

def display_calendar_view():
    st.header("Calendar View")
    
    # Date selection
    selected_date = st.date_input(
        "Select Date",
        st.session_state.selected_date
    )
    
    # Calendar integrations
    google_events = GoogleCalendarService().get_events(selected_date)
    apple_events = AppleCalendarService().get_events(selected_date)
    
    # Deduplicate events
    all_events = deduplicate_events(google_events + apple_events)
    
    # Display events
    st.subheader("Today's Events")
    for event in all_events:
        with st.expander(f"{event['start_time']} - {event['title']}"):
            st.write(f"Duration: {event['duration']}")
            st.write(f"Source: {event['source']}")

def display_task_management():
    st.header("Task Management")
    
    # Add new task
    with st.form("new_task"):
        task_title = st.text_input("Task Title")
        task_date = st.date_input("Task Date")
        task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submitted = st.form_submit_button("Add Task")
        
        if submitted and task_title:
            st.session_state.task_manager.add_task(task_title, task_date, task_priority)
            st.success("Task added successfully!")
    
    # Display tasks
    st.subheader("Your Tasks")
    tasks = st.session_state.task_manager.get_tasks()
    
    for task in tasks:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{task['title']}**")
        with col2:
            st.write(task['date'])
        with col3:
            status = st.selectbox(
                "Status",
                ["Not Started", "Partial", "Completed"],
                key=f"status_{task['id']}"
            )
            if status != task['status']:
                st.session_state.task_manager.update_task_status(task['id'], status)

def display_progress_analytics():
    st.header("Progress Analytics")
    
    # Time range selection
    time_range = st.selectbox(
        "Select Time Range",
        ["Last Week", "Last Month", "Last 3 Months"]
    )
    
    # Get task completion data
    completion_data = st.session_state.task_manager.get_completion_stats(time_range)
    
    # Display progress charts
    st.plotly_chart(create_progress_chart(completion_data))
    st.plotly_chart(create_trend_chart(completion_data))

if __name__ == "__main__":
    main()