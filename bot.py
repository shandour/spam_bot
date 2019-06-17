import logging

from decouple import config
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    Filters,
)

from commands import (
    init_db,
    start,
    unknown,
    info,
    currency_rates_with_args,
    log_error
)

from inline_query import inline_query


def main():
    token = config('BOT_TOKEN')
    debugging = config('DEBUG', cast=bool, default=True)

    logging.basicConfig(
        filename='logging.log',
        level=(logging.DEBUG if debugging else logging.WARNING)
    )
    init_db()
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # commands
    start_handler = CommandHandler(['start', 'introduction'], start)
    info_handler = CommandHandler(['info', 'howto', 'commands', 'about'], info)
    currency_rates_handler = CommandHandler(
        'currency',
        currency_rates_with_args
    )
    inline_handler = InlineQueryHandler(inline_query)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(inline_handler)
    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(currency_rates_handler)

    dispatcher.add_handler(unknown_handler)
    dispatcher.add_error_handler(log_error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
