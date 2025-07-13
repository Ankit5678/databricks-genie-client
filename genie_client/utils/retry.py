import time
import functools
from ..exceptions.custom_errors import RateLimitError, APIRequestError
from .constants import RATE_LIMIT_WAIT, MAX_RETRIES, RETRY_INTERVAL

def retry_api_call(func):
    """Decorator for API call retry logic"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except RateLimitError:
                wait_time = RATE_LIMIT_WAIT * (2 ** retries)
                time.sleep(min(wait_time, 300))  # Max 5 minutes
                retries += 1
            except APIRequestError as e:
                if e.status_code >= 500 and retries < MAX_RETRIES:
                    time.sleep(RETRY_INTERVAL * (2 ** retries))
                    retries += 1
                else:
                    raise
        return func(*args, **kwargs)  # Final attempt
    return wrapper