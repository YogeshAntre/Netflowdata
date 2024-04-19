from datetime import datetime
import pytz

def convert_date():

    your_timezone = pytz.timezone('Asia/Kolkata')

    # Get the current datetime in your local timezone
    local_now = datetime.now(your_timezone)

    # Format the local datetime as a string (if needed)
    formatted_local_now = local_now.isoformat().split('.')[0]

    return formatted_local_now