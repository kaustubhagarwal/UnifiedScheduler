import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_spending_pie_chart(spending_data):
    """Creates a pie chart showing spending by category"""
    fig = go.Figure(data=[go.Pie(
        labels=[item['category'] for item in spending_data],
        values=[item['total'] for item in spending_data],
        hole=.3,
        marker_colors=[item['color'] for item in spending_data]
    )])

    fig.update_layout(
        title="Spending by Category",
        showlegend=True,
        height=400
    )

    return fig

def create_balance_trend_chart(transactions, account_name=None):
    """Creates a line chart showing balance trends over time"""
    # Convert transactions to DataFrame for easier manipulation
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate running balance
    df = df.sort_values('date')
    df['running_balance'] = df['amount'].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['running_balance'],
        name=account_name or "Balance",
        line=dict(color='#00CC96')
    ))

    fig.update_layout(
        title="Balance Trend",
        xaxis_title="Date",
        yaxis_title="Balance",
        height=400
    )

    return fig

def create_income_expense_bar_chart(transactions):
    """Creates a bar chart comparing income vs expenses"""
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    
    # Group by month and type
    monthly_summary = df.groupby(['month', 'type'])['amount'].sum().reset_index()

    fig = go.Figure()

    for tx_type in ['Income', 'Expense']:
        data = monthly_summary[monthly_summary['type'] == tx_type]
        fig.add_trace(go.Bar(
            x=data['month'],
            y=data['amount'],
            name=tx_type,
            marker_color='#00CC96' if tx_type == 'Income' else '#EF553B'
        ))

    fig.update_layout(
        title="Monthly Income vs Expenses",
        xaxis_title="Month",
        yaxis_title="Amount",
        barmode='group',
        height=400
    )

    return fig

def create_daily_spending_chart(transactions):
    """Creates a line chart showing daily spending patterns"""
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    daily_spending = df.groupby('date')['amount'].sum().reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_spending['date'],
        y=daily_spending['amount'],
        mode='lines+markers',
        name="Daily Spending",
        line=dict(color='#FF4B4B')
    ))

    fig.update_layout(
        title="Daily Spending Pattern",
        xaxis_title="Date",
        yaxis_title="Amount Spent",
        height=400
    )

    return fig
