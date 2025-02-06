import streamlit as st
import datetime
from datetime import time
from services.google_calendar import GoogleCalendarService
from services.apple_calendar import AppleCalendarService
from services.task_manager import TaskManager
from visualization.progress_charts import create_progress_chart, create_trend_chart, create_priority_completion_chart, create_time_distribution_chart
from utils.deduplication import deduplicate_events
from models.database import get_db, TaskType, RecurrencePattern
import os

# Initialize database
next(get_db())

# Set page configuration
st.set_page_config(
    page_title="Calendar & Task Tracker",
    page_icon="📅",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .task-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .time-info {
        color: #9e9e9e;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
    if 'show_task_type' not in st.session_state:
        st.session_state.show_task_type = "Regular Task"

def main():
    initialize_session_state()

    # Create a container for the header
    with st.container():
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image("https://img.icons8.com/fluency/96/calendar.png", width=50)
        with col2:
            st.title("Calendar & Task Tracker")

    st.markdown("---")

    # Sidebar with improved styling
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "",
            ["📅 Calendar View", "✅ Task Management", "📊 Progress Analytics"],
            label_visibility="collapsed"
        )

    # Main content area
    if "Calendar" in page:
        display_calendar_view()
    elif "Task" in page:
        display_task_management()
    else:
        display_progress_analytics()

def display_calendar_view():
    st.header("📅 Calendar View")

    # Add calendar integration section
    with st.expander("🔄 Calendar Integration Setup", expanded=True):
        st.markdown("""
        ### Connect Your Calendars

        1. **Google Calendar**
        To connect your Google Calendar, you'll need to:
        1. Go to the [Google Cloud Console](https://console.cloud.google.com)
        2. Create a new project or select an existing one
        3. Enable the Google Calendar API
        4. Create OAuth 2.0 credentials
        5. Download the credentials file and rename it to 'credentials.json'
        6. Upload it using the file uploader below
        """)

        # File uploader for Google Calendar credentials
        uploaded_file = st.file_uploader("Upload Google Calendar credentials.json", type=['json'])
        if uploaded_file is not None:
            # Save the uploaded credentials file
            credentials_path = '.credentials'
            if not os.path.exists(credentials_path):
                os.makedirs(credentials_path)
            with open(os.path.join(credentials_path, 'credentials.json'), 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("Credentials uploaded successfully! Click 'Connect Google Calendar' to authenticate.")

        if st.button("Connect Google Calendar"):
            try:
                google_calendar = GoogleCalendarService()
                google_calendar.authenticate()
                st.success("Successfully connected to Google Calendar!")
            except Exception as e:
                st.error(f"Error connecting to Google Calendar: {str(e)}")

        st.markdown("""
        2. **Apple Calendar**
        To connect your Apple Calendar:
        1. Open System Preferences on your Mac
        2. Go to Internet Accounts
        3. Select your iCloud account
        4. Enable Calendar sharing
        """)
        if st.button("Connect Apple Calendar"):
            st.info("Apple Calendar integration requires additional system-level configuration. Please contact support for assistance.")

    # Rest of the calendar view code remains the same
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_date = st.date_input(
            "Select Date",
            st.session_state.selected_date,
            key="calendar_date"
        )

    # Calendar integrations
    google_events = GoogleCalendarService().get_events(selected_date)
    apple_events = AppleCalendarService().get_events(selected_date)

    # Deduplicate events
    all_events = deduplicate_events(google_events + apple_events)

    # Display events in a more attractive format
    st.subheader(f"Events for {selected_date.strftime('%B %d, %Y')}")

    if not all_events:
        st.info("No events scheduled for today")
    else:
        for event in all_events:
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h3>{event['title']}</h3>
                    <p>🕒 {event['start_time']} • {event['duration']}</p>
                    <p>📱 {event['source']}</p>
                </div>
                """, unsafe_allow_html=True)

def display_task_management():
    st.header("✅ Task Management")

    # Task type toggle
    task_type = st.radio(
        "View",
        ["Regular Tasks", "Daily Activities", "All Tasks"],
        horizontal=True
    )

    # Map selection to TaskType
    task_type_map = {
        "Regular Tasks": TaskType.REGULAR.value,
        "Daily Activities": TaskType.DAILY.value,
        "All Tasks": None
    }

    # Create two columns for task input and task list
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Add New Task")
        with st.form("new_task", clear_on_submit=True):
            task_title = st.text_input("Task Title")
            task_date = st.date_input("Task Date")
            task_type_input = st.selectbox(
                "Task Type",
                [TaskType.REGULAR.value, TaskType.DAILY.value]
            )

            task_priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                format_func=lambda x: {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}[x]
            )

            # Time constraints
            is_fixed_time = st.checkbox("Fixed Time Task")
            fixed_time = None
            flexible_start_time = None
            flexible_end_time = None
            estimated_duration = None

            if is_fixed_time:
                fixed_time = st.time_input("Fixed Time", time(9, 0))
                estimated_duration = st.number_input("Estimated Duration (minutes)", min_value=5, value=30)
            else:
                col3, col4 = st.columns(2)
                with col3:
                    flexible_start_time = st.time_input("Flexible Start Time", time(9, 0))
                with col4:
                    flexible_end_time = st.time_input("Flexible End Time", time(17, 0))
                estimated_duration = st.number_input("Estimated Duration (minutes)", min_value=5, value=30)

            # Recurrence pattern for daily activities
            recurrence_pattern = "None"
            if task_type_input == TaskType.DAILY.value:
                recurrence_pattern = st.selectbox(
                    "Recurrence Pattern",
                    [p.value for p in RecurrencePattern]
                )

            submitted = st.form_submit_button("Add Task", use_container_width=True)

            if submitted and task_title:
                st.session_state.task_manager.add_task(
                    title=task_title,
                    date=task_date,
                    priority=task_priority,
                    task_type=task_type_input,
                    is_fixed_time=is_fixed_time,
                    fixed_time=fixed_time,
                    flexible_start_time=flexible_start_time,
                    flexible_end_time=flexible_end_time,
                    recurrence_pattern=recurrence_pattern,
                    estimated_duration=estimated_duration
                )
                st.success("Task added successfully!")

    with col2:
        st.markdown("### Your Tasks")
        tasks = st.session_state.task_manager.get_tasks(task_type_map[task_type])

        if not tasks:
            st.info("No tasks added yet")
        else:
            for task in tasks:
                with st.container():
                    # Time information string
                    time_info = ""
                    if task['is_fixed_time'] and task['fixed_time']:
                        time_info = f"🕒 Fixed Time: {task['fixed_time']}"
                    elif task['flexible_start_time'] and task['flexible_end_time']:
                        time_info = f"🕒 Flexible Time: {task['flexible_start_time']} - {task['flexible_end_time']}"

                    st.markdown(f"""
                    <div class="task-card">
                        <h3>{task['title']}</h3>
                        <p>📅 {task['date']} • {get_priority_icon(task['priority'])} {task['priority']}</p>
                        <p class="time-info">{time_info}</p>
                        <p class="time-info">⏱️ Duration: {task['estimated_duration']} minutes</p>
                        <p class="time-info">🔄 {task['recurrence_pattern']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    status = st.select_slider(
                        "Progress",
                        options=["Not Started", "Partial", "Completed"],
                        value=task['status'],
                        key=f"status_{task['id']}"
                    )
                    if status != task['status']:
                        st.session_state.task_manager.update_task_status(task['id'], status)
                    st.markdown("---")

def display_progress_analytics():
    st.header("📊 Progress Analytics")

    # Create columns for filter and summary
    col1, col2 = st.columns([2, 1])

    with col1:
        time_range = st.select_slider(
            "Select Time Range",
            options=["Last Week", "Last Month", "Last 3 Months"],
            value="Last Week"
        )

    # Get task completion data
    completion_data = st.session_state.task_manager.get_completion_stats(time_range)

    # Display summary metrics
    total_tasks = (completion_data['completed'] + completion_data['partial'] + 
                  completion_data['not_started'])
    if total_tasks > 0:
        completion_rate = (completion_data['completed'] / total_tasks) * 100

        # Create metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Completion Rate", f"{completion_rate:.1f}%")
        with col2:
            st.metric("Total Tasks", total_tasks)
        with col3:
            st.metric("Completed Tasks", completion_data['completed'])

        # Priority-based metrics
        st.subheader("Priority-based Performance")
        for priority, stats in completion_data['priority_stats'].items():
            if stats['total'] > 0:
                priority_completion = (stats['completed'] / stats['total']) * 100
                st.metric(
                    f"{priority} Priority Tasks",
                    f"{priority_completion:.1f}%",
                    f"{stats['completed']}/{stats['total']} completed"
                )

        # Display charts in tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overall Progress",
            "🎯 Priority Analysis",
            "📈 Trends",
            "⏰ Time Distribution"
        ])

        with tab1:
            st.plotly_chart(create_progress_chart(completion_data), use_container_width=True)

        with tab2:
            st.plotly_chart(create_priority_completion_chart(completion_data), use_container_width=True)

        with tab3:
            st.plotly_chart(create_trend_chart(completion_data), use_container_width=True)

        with tab4:
            st.plotly_chart(create_time_distribution_chart(completion_data), use_container_width=True)

            # Best performing days
            st.subheader("Best Performing Days")
            day_stats = completion_data['day_stats']
            for day, stats in day_stats.items():
                if stats['total'] > 0:
                    completion_rate = (stats['completed'] / stats['total']) * 100
                    st.text(f"{day}: {completion_rate:.1f}% completion rate ({stats['completed']}/{stats['total']})")


def get_priority_icon(priority):
    icons = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢"
    }
    return icons.get(priority, "")

if __name__ == "__main__":
    main()