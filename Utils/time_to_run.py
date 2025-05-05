'''
This module tracks the time between an initial call and subsequent calls
and prints the delta in a human-readable format.
'''
from datetime import datetime


def ttr(time=None, suppress_output=False):
    '''
    time to run
    '''
    if time is None:
        return datetime.now()


    delta = datetime.now() - time
    total_seconds = delta.total_seconds()

    if total_seconds < 600:  # Less than 10 minutes
        result = f"{total_seconds:.2f} seconds"
    elif total_seconds < 18000:  # Less than 5 hours
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        result = f"{minutes:02d}:{seconds:02d} (mm:ss)"
    elif total_seconds < 432000:  # Less than 5 days
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        result = f"{hours:02d}:{minutes:02d}:{seconds:02d} (hh:mm:ss)"
    else:  # 5 days or more
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        result = f"{days} {hours:02d}:{minutes:02d}:{seconds:02d} (days hh:mm:ss)"

    if not suppress_output:
        print(result)
    return result
