from datetime import datetime
from functools import lru_cache, wraps

import requests

from consts import allowed_currency_symbols_lst

currency_rates_url = 'https://api.exchangeratesapi.io'


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
def get_currency_rates(**kwargs):
    success = True
    url = currency_rates_url

    params = {
        'base': kwargs.get('base', 'EUR'),
        'date': kwargs.get('date'),
        'symbols': kwargs.get('currencies')
    }

    if params.get('date'):
        url += f'/{params["date"]}'
    else:
        url += '/latest'

    resp = requests.get(url, params)
    if resp.ok:
        res = resp.json()
        text = f'Date: {res.get("date")}\nBase: {params["base"]}\n'
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
        error = resp.json()['error']
        text = f'Sorry, unable to answer your query. Reason: {error}'

    return text, success


# TODO: add normal validation and parsing
def parse_currency_args(lst):
    params_dct = {}
    relevant_args_lst = ['base', 'currencies', 'date']
    for arg in relevant_args_lst:
        try:
            pos = lst.index(arg)
            if arg == 'base':
                base = lst[pos+1].upper()
                params_dct[arg] = (
                    base
                    if base in allowed_currency_symbols_lst
                    else 'EUR'
                )
            elif arg == 'currencies':
                params_dct[arg] = ''
                for item in lst[pos+1:]:
                    item = item.upper()
                    if item in allowed_currency_symbols_lst:
                        params_dct[arg] += f'{item},'
                    else:
                        break
                params_dct[arg] = params_dct[arg].rstrip(',')
            elif arg == 'date':
                # check if it conforms to the format
                datetime.strptime(lst[pos+1], '%Y-%m-%d')
                params_dct[arg] = lst[pos+1]
        except (ValueError, IndexError):
            continue

    return params_dct
