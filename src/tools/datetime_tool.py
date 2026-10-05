from datetime import datetime

def get_current_datetime() -> str:
    return datetime.now().isoformat()

