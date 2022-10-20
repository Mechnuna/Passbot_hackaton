from adatabaselib.core.configs import F_TimeConfig
from datetime import datetime
from pytz import tzinfo
from time import time


def decorator_timeit(function):
    """
    Декоратор. Подсчет времени выполнения
    """
    def wrapper(*args, **kwargs):
        start_time = time()
        result = function(*args, **kwargs)
        print(time() - start_time)
        return result
    
    return wrapper


defaut_time = F_TimeConfig()

def get_time(tz: tzinfo = defaut_time.timezone):
    return datetime.now(tz=tz)
