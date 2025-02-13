import streamlit as st
from datetime import datetime, time, date, timedelta
from services.google_calendar import GoogleCalendarService
from services.apple_calendar import AppleCalendarService
from services.task_manager import TaskManager
from visualization.progress_charts import create_progress_chart, create_trend_chart, create_priority_completion_chart, create_time_distribution_chart
from utils.deduplication import deduplicate_events
from models.database import get_db, TaskType, RecurrencePattern
import os
from services.ai_prioritization import AIPrioritization
from services.gamification import GamificationService
import json
import plotly.express as px
from services.finance_manager import FinanceManager
from visualization.finance_charts import (
    create_spending_pie_chart, create_balance_trend_chart,
    create_income_expense_bar_chart, create_daily_spending_chart
)
from models.finance import AccountType, TransactionType

# Initialize database
from models.database import Base, engine
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/calendar']
)

# Ensure tables are created before running the app
Base.metadata.create_all(bind=engine)

# Set page configuration
st.set_page_config(
    page_title="Calendar & Task Tracker",
    page_icon="📅",
    layout="wide"
)

# Initialize AI and gamification services
if 'ai_prioritization' not in st.session_state:
    st.session_state.ai_prioritization = AIPrioritization()
if 'gamification' not in st.session_state:
    st.session_state.gamification = GamificationService()
if 'user_stats' not in st.session_state:
    st.session_state.user_stats = {
        'points': 0,
        'daily_streak': 0,
        'weekly_streak': 0,
        'achievements': [],
        'last_active': datetime.now().isoformat()
    }

# Initialize finance manager in session state
if 'finance_manager' not in st.session_state:
    st.session_state.finance_manager = FinanceManager()

# Enhanced CSS with animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

    .main {
        font-family: 'Poppins', sans-serif;
        padding: 2rem;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(45deg, #FF4B4B, #FF7676);
        border: none;
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.3);
    }

    .task-card {
        background: linear-gradient(145deg, #2a2d3a, #1e2029);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .task-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }

    .time-info {
        color: #9e9e9e;
        font-size: 0.9em;
        margin-top: 0.5rem;
    }

    .achievement-card {
        background: linear-gradient(145deg, #3d4250, #2a2d3a);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #FF4B4B;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 5px #FF4B4B, 0 0 10px #FF4B4B;
        }
        to {
            box-shadow: 0 0 10px #FF4B4B, 0 0 20px #FF4B4B;
        }
    }

    .stats-card {
        background: linear-gradient(145deg, #2a2d3a, #1e2029);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        text-align: center;
    }

    .streak-count {
        font-size: 2em;
        font-weight: 600;
        color: #FF4B4B;
    }

    .points-count {
        font-size: 1.5em;
        color: #00CC96;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date.today()
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
            ["📅 Calendar View", "✅ Task Management", "💰 Finance Tracker", "📊 Progress Analytics"],
            label_visibility="collapsed"
        )
        display_user_stats()


    # Main content area
    if "Calendar" in page:
        display_calendar_view()
    elif "Task" in page:
        display_task_management()
    elif "Finance" in page:
        display_finance_tracker()
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

    # Rest of the calendar view code 
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
                    update_task_status(task['id'], status)

                    # Delete button with refresh logic
                    if st.button(f"Delete Task", key=f"delete_{task['id']}"):
                        success = st.session_state.task_manager.delete_task(task['id'])
                        if success:
                            st.success(f"Task '{task['title']}' deleted successfully!")
                            # Use one of the solutions below:
                            # Solution 1: Update query params for refresh
                            st.experimental_set_query_params(refresh=True)
                            # Solution 2: Use JavaScript for full reload (optional)
                            # st.write('<script>location.reload()</script>', unsafe_allow_html=True)
                        else:
                            st.error("Failed to delete the task.")

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

def display_user_stats():
    """Display user statistics and achievements"""
    st.sidebar.markdown("### 🏆 Your Progress")

    # Display points and streaks
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="stats-card">
                <h4>Daily Streak</h4>
                <div class="streak-count">🔥 {st.session_state.user_stats['daily_streak']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="stats-card">
                <h4>Points</h4>
                <div class="points-count">✨ {st.session_state.user_stats['points']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Display achievements
    if st.session_state.user_stats['achievements']:
        st.sidebar.markdown("### 🎯 Achievements")
        for achievement in st.session_state.user_stats['achievements']:
            st.sidebar.markdown(
                f"""
                <div class="achievement-card">
                    <h4>{achievement['name']}</h4>
                    <p>{achievement['description']}</p>
                    <p>+{achievement['points']} points</p>
                </div>
                """,
                unsafe_allow_html=True
            )

def update_task_status(task_id: str, new_status: str):
    """Update task status and handle gamification"""
    task = next((t for t in st.session_state.task_manager.get_tasks() if t['id'] == task_id), None)
    if task and task['status'] != new_status:
        # Update task status
        st.session_state.task_manager.update_task_status(task_id, new_status)

        # Calculate and award points
        points = st.session_state.gamification.calculate_points(task, new_status)
        st.session_state.user_stats['points'] += points

        # Update streaks
        st.session_state.user_stats = st.session_state.gamification.update_streak(
            st.session_state.user_stats
        )

        # Check for new achievements
        new_achievements = st.session_state.gamification.check_achievements(
            st.session_state.user_stats,
            st.session_state.task_manager.get_tasks()
        )

        if new_achievements:
            for achievement in new_achievements:
                st.session_state.user_stats['achievements'].append(achievement)
                st.session_state.user_stats['points'] += achievement['points']
                st.success(f"🎉 New Achievement Unlocked: {achievement['name']}!")


def display_finance_tracker():
    st.header("💰 Finance Tracker")

    # Create tabs for different finance sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "💳 Accounts & Balances",
        "📝 Transactions",
        "📊 Analytics",
        "⚙️ Categories"
    ])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Add New Account")
            with st.form("new_account", clear_on_submit=True):
                account_name = st.text_input("Account Name")
                account_type = st.selectbox(
                    "Account Type",
                    [type.value for type in AccountType]
                )
                initial_balance = st.number_input("Initial Balance", value=0.0)
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP"])
                description = st.text_area("Description")

                if st.form_submit_button("Add Account"):
                    st.session_state.finance_manager.add_account(
                        account_name, account_type, initial_balance,
                        currency, description
                    )
                    st.success("Account added successfully!")

        with col2:
            st.subheader("Net Worth")
            net_worth = st.session_state.finance_manager.get_net_worth()
            st.markdown(f"""
            <div class="stats-card">
                <h3>Total Net Worth</h3>
                <div class="points-count">${net_worth:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("Your Accounts")
        accounts = st.session_state.finance_manager.get_accounts()
        for account in accounts:
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h3>{account['name']}</h3>
                    <p>Type: {account['type']}</p>
                    <p>Balance: {account['currency']} {account['balance']:,.2f}</p>
                    <p class="time-info">{account['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Add a delete button for each account
                if st.button(f"Delete {account['name']}", key=f"delete_{account['id']}"):
                    success = st.session_state.finance_manager.delete_account(account['id'])
                    if success:
                        st.success(f"Account '{account['name']}' deleted successfully!")
                        st.experimental_set_query_params(refresh=True)
                    else:
                        st.error(f"Failed to delete account '{account['name']}'.")


    with tab2:
        st.subheader("Add Transaction")
        with st.form("new_transaction", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                account = st.selectbox(
                    "Account",
                    options=[acc['id'] for acc in accounts],
                    format_func=lambda x: next((acc['name'] for acc in accounts if acc['id'] == x), "")
                )
                transaction_type = st.selectbox(
                    "Transaction Type",
                    [type.value for type in TransactionType]
                )

            with col2:
                categories = st.session_state.finance_manager.get_categories()
                category = st.selectbox(
                    "Category",
                    options=[cat['id'] for cat in categories],
                    format_func=lambda x: next((cat['name'] for cat in categories if cat['id'] == x), "")
                )
                amount = st.number_input("Amount", min_value=0.0, value=0.0)

            description = st.text_area("Description")
            date = st.date_input("Date")

            if st.form_submit_button("Add Transaction"):
                transaction_date = datetime.combine(date, time.min)
                st.session_state.finance_manager.add_transaction(
                    account, category, transaction_type, amount,
                    description, transaction_date
                )
                st.success("Transaction added successfully!")

        st.subheader("Recent Transactions")
        transactions = st.session_state.finance_manager.get_transactions()
        for transaction in transactions:
            st.markdown(f"""
            <div class="task-card">
                <h3>{transaction['description'] or transaction['type']}</h3>
                <p>Amount: ${abs(transaction['amount']):,.2f}</p>
                <p>Category: {transaction['category']}</p>
                <p class="time-info">Account: {transaction['account']} • {transaction['date']}</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader("Financial Analytics")

        # Time range selector for analytics
        time_range = st.selectbox(
            "Select Time Range",
            ["Last Week", "Last Month", "Last 3 Months", "Last Year"]
        )

        # Calculate date range
        end_date = datetime.now()
        if time_range == "Last Week":
            start_date = end_date - timedelta(days=7)
        elif time_range == "Last Month":
            start_date = end_date - timedelta(days=30)
        elif time_range == "Last 3 Months":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)

        # Get filtered transactions
        filtered_transactions = st.session_state.finance_manager.get_transactions(
            start_date=start_date,
            end_date=end_date
        )

        # Display charts
        col1, col2 = st.columns(2)
        with col1:
            spending_data = st.session_state.finance_manager.get_spending_by_category(
                start_date, end_date
            )
            st.plotly_chart(
                create_spending_pie_chart(spending_data),
                use_container_width=True,
                key="spending_pie_chart"
            )

        with col2:
            st.plotly_chart(
                create_balance_trend_chart(filtered_transactions),
                use_container_width=True,
                key="balance_trend_chart"
            )

        st.plotly_chart(
            create_income_expense_bar_chart(filtered_transactions),
            use_container_width=True,
            key="income_expense_chart"
        )

        st.plotly_chart(
            create_daily_spending_chart(filtered_transactions),
            use_container_width=True,
            key="daily_spending_chart"
        )

    with tab4:
        st.subheader("Add Category")
        with st.form("new_category", clear_on_submit=True):
            category_name = st.text_input("Category Name")
            category_color = st.color_picker("Category Color", "#00CC96")
            category_description = st.text_area("Description")

            if st.form_submit_button("Add Category"):
                st.session_state.finance_manager.add_category(
                    category_name, category_color, category_description
                )
                st.success("Category added successfully!")

        st.subheader("Existing Categories")
        categories = st.session_state.finance_manager.get_categories()
        for category in categories:
            st.markdown(f"""
            <div class="task-card">
                <h3>{category['name']}</h3>
                <p>Color: <span style="color: {category['color']}>■</span></p>
                <p class="time-info">{category['description']}</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
