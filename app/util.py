from datetime import datetime
import random

def get_current_timestamp_for_db():
    """
    Returns the current timestamp as a string formatted for SQL TIMESTAMP insert,
    e.g. 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_user_id():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 digits
    random_part = random.randint(100, 999) # 3 digits
    return f"{timestamp}{random_part}"