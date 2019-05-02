from datetime import datetime

import requests
from sqlalchemy import and_, select

from consts import allowed_currency_symbols_lst
from db import currency_rates, engine

currency_rates_url = 'https://api.exchangeratesapi.io'


def get_currency_rates(**kwargs):
    text = ''
    res = {}
    params = {
        'base': kwargs.get('base', 'EUR'),
        'date': kwargs.get('date', datetime.utcnow().date()),
        'symbols': kwargs.get('currencies')
    }

    with engine.connect() as conn:
        query = conn.execute(
            select([
                currency_rates.c.rates,
                currency_rates.c.lookup_date,
                currency_rates.c.base,
            ]).where(and_(
                currency_rates.c.base == params['base'],
                currency_rates.c.lookup_date == params['date'],
            ))
        )

    result = query.fetchone()

    if result:
        print('RESULT')
        res = {
            'rates': result[0],
            'date': result[1],
            'base': result[2],
        }
    else:
        print('WUUUUT')
        url = currency_rates_url
        if params.get('date') != datetime.utcnow().date():
            url += f'/{params["date"]}'
        else:
            params.pop('date', None)
            url += '/latest'

            resp = requests.get(url, params)
            if resp.ok:
                res = resp.json()
                with engine.connect() as conn:
                    # sometimes the api sends a previous date
                    # for /latest with querystrings
                    existing_record = conn.execute(
                        select([currency_rates.c.base])
                        .where(
                            and_(
                                currency_rates.c.base == res['base'],
                                currency_rates.c.lookup_date == res['date'],
                            )
                        )).fetchone()
                    if not existing_record:
                        conn.execute(
                            currency_rates.insert().values(
                                base=res['base'],
                                lookup_date=res['date'],
                                rates=res['rates']
                            )
                        )
            else:
                error = resp.json()['error']
                return f'Sorry, unable to answer your query. Reason: {error}'

    text = f'Date: {res["date"]}\nBase: {res["base"]}\n'
    symbols = params.get('symbols')
    for cur, rate in res['rates'].items():
        if symbols and cur not in symbols:
            continue
        text += f'{cur}: {rate}\n'

    return text


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
