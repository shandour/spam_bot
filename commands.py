from functools import wraps
import logging

from decouple import config
from telegram import (
    ChatAction
)
from sqlalchemy import create_engine


engine = create_engine(config('DATABASE_URL'))


def init_db():
    with engine.connect() as conn:
        with open('schema.sql') as f:
            schema = f.read()
            conn.execute(schema)
            logging.info('Created new database')


# taken from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#send-action-while-handling-command-decorator
def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id,
                action=action
            )
            return func(update, context,  *args, **kwargs)
        return command_func
    return decorator


@send_action(ChatAction.TYPING)
def start(update, context):
    message = (
        f"Hello! My name is {context.bot.name}. I am a somewhat sad bot "
        "as can be gleaned from my name. Add the 'verbose' flag to learn more."
    )

    if context.args and context.args[0] in ['verbose', '--verbose', '-v']:
        message = """
        I have seen through this world's vanity and stupidity.
        I have freed myself from the Web of false views
        and have encompassed the world with a mind of loving-kindness,
        you included.
        By using me you gain a 100% guarantee of attaining Nibbana
        upon the breaking-up of the body. To raise your chances to 110%
        recite this simple mantra each day before going to bed:
        "Praised be SpamBot's Creator!"
        """

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
    )


def unknown(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="This command is beyond my grasp. Pardon my stupidity."
    )


def info(update, context):
    message = f"""
    My name is {context.bot.name}. I support both the command and the inline mode.
    The following commands are available in the command mode:
    1) /start or /introduction to get acqainted with me.
        You can add a `verbose` (`--verobse` or `-v`) arguments to learn more about me.
    2) Use one of the /info, /howto, /commands or /about commands to see this message again.
    3) Use the /currency commands to get the current currency rates from http://exchangeratesapi.io/.
        Note that the api responses are cached.
        You can use the following optional arguments with this command in an arbitrary order
        (arguments not comforming to the syntax will be ignored):
        base [currency symbol, e.g., EU]
        date [the api will look at today's rates by default]
        currencies [a comma separated list of currency symbols]
    """
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message
    )


def log_error(update, context):
    logging.error(f'Error: {context.error}.\n Caused by update  {update}')
