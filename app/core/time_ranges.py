from datetime import datetime, timedelta
import pytz

def get_time_context():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    today = now.date()
    yesterday = today - timedelta(days=1)
    
    # Last month
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    
    # Last week (Monday-Sunday)
    # today.weekday() is 0 for Monday, 6 for Sunday
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)
    end_of_last_week = start_of_this_week - timedelta(days=1)
    
    # This year
    start_of_year = today.replace(month=1, day=1)
    
    context = (
        f"Current Date: {today}\n"
        f"Today: {today}\n"
        f"Yesterday: {yesterday}\n"
        f"Last Month Range: {first_day_last_month} to {last_day_last_month}\n"
        f"Last Week Range (Mon-Sun): {start_of_last_week} to {end_of_last_week}\n"
        f"This Year Range: {start_of_year} to {today}\n"
        f"This Month Range: {first_day_this_month} to {today}\n"
    )
    return context

if __name__ == "__main__":
    print(get_time_context())
