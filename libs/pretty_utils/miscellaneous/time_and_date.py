import time
from datetime import (
    datetime,
    timezone,
)


def get_izoformat_timestamp() -> str:
    """
    Get the current timestamp.

    Returns:
        str: the current timestamp.

    """
    return datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'

def get_unix_timestamp() -> str:
    return str(int(time.time() * 1000))
