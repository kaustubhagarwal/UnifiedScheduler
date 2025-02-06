import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def create_progress_chart(completion_data):
    """
    Creates a pie chart showing task completion status
    """
    labels = ['Completed', 'Partial', 'Not Started']
    values = [
        completion_data['completed'],
        completion_data['partial'],
        completion_data['not_started']
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#00CC96', '#FFA15A', '#EF553B']
    )])

    fig.update_layout(
        title="Task Completion Status",
        showlegend=True,
        height=400
    )

    return fig

def create_trend_chart(completion_data):
    """
    Creates a line chart showing task completion trends over time
    """
    tasks = completion_data['tasks']
    dates = []
    completed_counts = []
    partial_counts = []

    # Group tasks by date
    date_stats = {}
    for task in tasks:
        task_date = datetime.fromisoformat(task['date']).date()
        if task_date not in date_stats:
            date_stats[task_date] = {'completed': 0, 'partial': 0}

        if task['status'] == 'Completed':
            date_stats[task_date]['completed'] += 1
        elif task['status'] == 'Partial':
            date_stats[task_date]['partial'] += 1

    # Sort dates and prepare data for plotting
    for date in sorted(date_stats.keys()):
        dates.append(date)
        completed_counts.append(date_stats[date]['completed'])
        partial_counts.append(date_stats[date]['partial'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=completed_counts,
        name="Completed",
        line=dict(color='#00CC96')
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=partial_counts,
        name="Partial",
        line=dict(color='#FFA15A')
    ))

    fig.update_layout(
        title="Task Completion Trends",
        xaxis_title="Date",
        yaxis_title="Number of Tasks",
        height=400
    )

    return fig

def create_priority_completion_chart(completion_data):
    """
    Creates a bar chart showing completion rates by priority
    """
    priorities = {'High': [], 'Medium': [], 'Low': []}

    for task in completion_data['tasks']:
        priorities[task['priority']].append(task['status'])

    fig = go.Figure()

    for priority in priorities:
        total = len(priorities[priority])
        if total > 0:
            completed = len([s for s in priorities[priority] if s == 'Completed'])
            partial = len([s for s in priorities[priority] if s == 'Partial'])
            not_started = total - completed - partial

            fig.add_trace(go.Bar(
                name=priority,
                x=['Completed', 'Partial', 'Not Started'],
                y=[completed, partial, not_started],
                text=[f"{(v/total)*100:.1f}%" for v in [completed, partial, not_started]],
                textposition='auto',
            ))

    fig.update_layout(
        title="Task Completion by Priority",
        barmode='group',
        height=400,
        yaxis_title="Number of Tasks"
    )

    return fig

def create_time_distribution_chart(completion_data):
    """
    Creates a scatter plot showing task distribution across time
    """
    tasks = completion_data['tasks']
    fixed_times = []
    flexible_times = []

    for task in tasks:
        if task.get('is_fixed_time') and task.get('fixed_time'):
            fixed_times.append({
                'time': task['fixed_time'],
                'title': task['title'],
                'status': task['status'],
                'priority': task['priority']
            })
        elif task.get('flexible_start_time'):
            flexible_times.append({
                'start': task['flexible_start_time'],
                'end': task['flexible_end_time'],
                'title': task['title'],
                'status': task['status'],
                'priority': task['priority']
            })

    fig = go.Figure()

    # Add fixed time tasks
    if fixed_times:
        times = [datetime.strptime(t['time'], '%H:%M').hour + 
                datetime.strptime(t['time'], '%H:%M').minute/60 for t in fixed_times]
        fig.add_trace(go.Scatter(
            x=times,
            y=[1]*len(times),
            mode='markers',
            name='Fixed Time Tasks',
            text=[f"{t['title']} ({t['priority']})" for t in fixed_times],
            marker=dict(
                size=10,
                color=['#00CC96' if t['status'] == 'Completed' else '#FFA15A' 
                       if t['status'] == 'Partial' else '#EF553B' for t in fixed_times]
            )
        ))

    fig.update_layout(
        title="Task Time Distribution",
        xaxis_title="Hour of Day",
        yaxis_showticklabels=False,
        height=300,
        showlegend=True
    )

    return fig