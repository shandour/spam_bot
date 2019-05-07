import random
import uuid

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import MAX_MESSAGE_LENGTH
from sqlalchemy import select

from db import sermons, engine
from utils import get_currency_rates


def sermon_answerer():
    defaut_sermon = 'Namo tassa bhagavato arahato sammāsambuddhassā.'
    sermon = ''
    with engine.connect() as conn:
        ids = conn.execute(select([sermons.c.id])).fetchall()
        if ids:
            sermon = conn.execute(
                select([sermons.c.sermon_text])
                .where(sermons.c.id == random.choice(ids)[0])
            ).fetchone()

    if not sermon or not sermon[0].strip():
        sermon = defaut_sermon
    else:
        sermon = sermon[0]

    if len(sermon) > MAX_MESSAGE_LENGTH:
        sermon = sermon[:MAX_MESSAGE_LENGTH-3] + '...'

    return [
        InlineQueryResultArticle(
            id=f'{uuid.uuid4()}',
            title='SERMON',
            input_message_content=InputTextMessageContent(
                sermon
            )
        )
    ]


def get_latest_CEB_currency_rates():
    rates = get_currency_rates()
    return [
        InlineQueryResultArticle(
            id=f'{uuid.uuid4()}',
            title='LATEST CURRENCY RATES',
            input_message_content=InputTextMessageContent(
                rates
            )
        )
    ]


def inline_query(update, context):
    # the defult as per the docs
    cache_results = 300
    query = update.inline_query.query
    results = []
    if not query:
        return
    if query.lower() == 'sermon':
        results = sermon_answerer()
        cache_results = 0
    elif query.lower() == 'currency':
        results = get_latest_CEB_currency_rates()

    if results:
        context.bot.answer_inline_query(
            update.inline_query.id,
            results,
            cache_results,
        )
    else:
        results = [
            InlineQueryResultArticle(
                id='no_results',
                title='Commands Info',
                input_message_content=InputTextMessageContent(
                    'Available commands are: sermon, currency'
                )
            )
        ]
        context.bot.answer_inline_query(
            update.inline_query.id,
            results,
            cache_results,
        )
