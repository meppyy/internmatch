from datetime import datetime
from zoneinfo import ZoneInfo


INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def current_ist_date():
    """Return the current calendar date in Indian Standard Time."""
    return datetime.now(INDIA_TIMEZONE).date()