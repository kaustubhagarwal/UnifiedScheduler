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
