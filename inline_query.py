import random

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import MAX_MESSAGE_LENGTH
from sqlalchemy import select

from commands import engine
from db import cermons
from utils import get_currency_rates


def cermon_answerer():
    defaut_cermon = 'Namo tassa bhagavato arahato sammāsambuddhassā.'
    cermon = ''

    with engine.connect() as conn:
        ids = conn.execute(select([cermons.c.id])).fetchall()
        if ids:
            cermon = conn.execute(
                select([cermons.c.cermon_text])
                .where(cermons.c.id == random.choice(ids)[0])
            ).fetchone()

    if not cermon or not cermon[0].strip():
        cermon = defaut_cermon
    if len(cermon) > MAX_MESSAGE_LENGTH:
        cermon = cermon[:MAX_MESSAGE_LENGTH-3] + '...'

    return [
        InlineQueryResultArticle(
            id='cermon',
            title='CERMON',
            input_message_content=InputTextMessageContent(
                cermon
            )
        )
    ]


def get_latest_CEB_currency_rates():
    # rates = get_currency_rates()
    print('WUT')
    rates, success = get_currency_rates()

    return [
        InlineQueryResultArticle(
            id='currency',
            title='LATEST CURRENCY RATES',
            input_message_content=InputTextMessageContent(
                rates
            )
        )
    ]


def inline_query(update, context):
    query = update.inline_query.query
    results = []
    if not query:
        return
    if query.lower() == 'cermon':
        results = cermon_answerer()
    elif query.lower() == 'currency':
        results = get_latest_CEB_currency_rates()

    if results:
        context.bot.answer_inline_query(update.inline_query.id, results)
    else:
        results = [
            InlineQueryResultArticle(
                id='no_results',
                title='Commands Info',
                input_message_content=InputTextMessageContent(
                    'Available commands are: cermon, currency'
                )
            )
        ]
        context.bot.answer_inline_query(update.inline_query.id, results)
