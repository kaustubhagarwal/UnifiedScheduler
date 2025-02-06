import datetime

def get_date_range(time_range):
    """
    Returns start and end dates based on the selected time range
    """
    today = datetime.date.today()
    
    if time_range == "Last Week":
        start_date = today - datetime.timedelta(days=7)
    elif time_range == "Last Month":
        start_date = today - datetime.timedelta(days=30)
    else:  # Last 3 Months
        start_date = today - datetime.timedelta(days=90)
    
    return start_date, today

def format_date(date):
    """
    Returns a formatted date string
    """
    return date.strftime("%Y-%m-%d")
