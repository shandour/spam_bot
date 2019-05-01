from datetime import datetime
from functools import lru_cache, wraps

import requests


currency_rates_url = 'https://api.exchangeratesapi.io/latest'


# cash api responses for the current date
def cache_to_expire_next_day(check_success=False):
    def wrapper(f):
        cash_date = datetime.utcnow().date()
        f = lru_cache(maxsize=None)(f)

        @wraps(f)
        def wrapped(*args, **kwargs):
            nonlocal cash_date
            nonlocal check_success
            current_date = datetime.utcnow().date()
            if cash_date < current_date:
                f.cache_clear()

            result = f(*args, **kwargs)
            if check_success:
                success = result[1]
                result = result[0]
                if not success:
                    f.cache_clear()
            return result
        return wrapped
    return wrapper


@cache_to_expire_next_day(check_success=True)
def get_currency_rates(base='EUR', check_success=True):
    print('QUERrrrrrY')
    success = True
    resp = requests.get(currency_rates_url, {'base': base})
    if resp.ok:
        res = resp.json()
        text = f'Base: {base}\n'
        try:
            for cur, rate in res['rates'].items():
                text += f'{cur}: {rate}\n'
        except KeyError:
            text = 'Sorry, the server returned an invalid response payload.'
            success = False
        except Exception as e:
            get_currency_rates.cache_clear()
            raise e
    else:
        error = res.json()['error']
        text = f'Sorry, unable to answer your query. Reason: {error}'

    return text, success
