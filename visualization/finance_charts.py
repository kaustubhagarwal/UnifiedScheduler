import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_spending_pie_chart(spending_data):
    """Creates a pie chart showing spending by category"""
    if not spending_data:
        return go.Figure().update_layout(
            title="No spending data available",
            height=400
        )

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

def create_balance_trend_chart(transactions):
    """Creates a line chart showing balance trends over time"""
    if not transactions:
        return go.Figure().update_layout(
            title="No transaction data available",
            height=400
        )

    # Convert transactions list to DataFrame
    df = pd.DataFrame(transactions)

    # Parse the ISO format date string to datetime
    df['parsed_date'] = pd.to_datetime([tx['date'] for tx in transactions])

    # Sort by date
    df = df.sort_values('parsed_date')

    # Calculate running balance
    df['running_balance'] = pd.to_numeric(df['amount']).cumsum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['parsed_date'],
        y=df['running_balance'],
        name="Balance",
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
    if not transactions:
        return go.Figure().update_layout(
            title="No transaction data available",
            height=400
        )

    # Convert transactions to DataFrame
    df = pd.DataFrame(transactions)

    # Parse dates
    df['parsed_date'] = pd.to_datetime([tx['date'] for tx in transactions])
    df['month'] = df['parsed_date'].dt.strftime('%Y-%m')

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
    if not transactions:
        return go.Figure().update_layout(
            title="No transaction data available",
            height=400
        )

    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Parse dates
    df['parsed_date'] = pd.to_datetime([tx['date'] for tx in transactions])

    # Calculate daily spending
    daily_spending = df.groupby('parsed_date')['amount'].sum().reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_spending['parsed_date'],
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