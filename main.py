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
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.date.today()

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

    # Create columns for date selection and filters
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

    # Create two columns for task input and task list
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Add New Task")
        with st.form("new_task", clear_on_submit=True):
            task_title = st.text_input("Task Title")
            task_date = st.date_input("Task Date")
            task_priority = st.selectbox(
                "Priority",
                ["High", "Medium", "Low"],
                format_func=lambda x: {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}[x]
            )
            submitted = st.form_submit_button("Add Task", use_container_width=True)

            if submitted and task_title:
                st.session_state.task_manager.add_task(task_title, task_date, task_priority)
                st.success("Task added successfully!")

    with col2:
        st.markdown("### Your Tasks")
        tasks = st.session_state.task_manager.get_tasks()

        if not tasks:
            st.info("No tasks added yet")
        else:
            for task in tasks:
                with st.container():
                    st.markdown(f"""
                    <div class="task-card">
                        <h3>{task['title']}</h3>
                        <p>📅 {task['date']} • {get_priority_icon(task['priority'])} {task['priority']}</p>
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
        st.metric("Task Completion Rate", f"{completion_rate:.1f}%")

    # Display charts in tabs
    tab1, tab2 = st.tabs(["📊 Progress Overview", "📈 Trends"])

    with tab1:
        st.plotly_chart(create_progress_chart(completion_data), use_container_width=True)

    with tab2:
        st.plotly_chart(create_trend_chart(completion_data), use_container_width=True)

def get_priority_icon(priority):
    icons = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢"
    }
    return icons.get(priority, "")

if __name__ == "__main__":
    main()