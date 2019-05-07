from datetime import datetime

from decouple import config
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


engine = sa.create_engine(config('DATABASE_URL'))

metadata = sa.MetaData()

chats = sa.Table('chats', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('telegram_id', sa.Integer, nullable=False),
                 sa.Column('chat_type', sa.String(50)),
                 sa.Column('username', sa.String(200)),
                 sa.Column('first_name', sa.String(200)))


notes = sa.Table('notes', metadata,
                 sa.Column('id', UUID(as_uuid=True), primary_key=True),
                 sa.Column(
                     'chat_id',
                     sa.ForeignKey(chats.c.telegram_id),
                     nullable=False
                 ),
                 sa.Column('note_text', sa.Text, nullable=False),
                 sa.Column('note_time', sa.DateTime, default=datetime.utcnow),
                 sa.Column('created', sa.DateTime, default=datetime.utcnow))

sermons = sa.Table('cermons', metadata,
                   sa.Column('id', sa.Integer, primary_key=True),
                   sa.Column('meta_info', sa.String(200)),
                   sa.Column('title', sa.String(200)),
                   sa.Column('sutta', sa.String(200)),
                   sa.Column('sermon_text', sa.Text, nullable=False))

currency_rates = sa.Table('currency_rates', metadata,
                          sa.Column('rates', sa.JSON, nullable=False),
                          sa.Column('base', sa.String(10), primary_key=True),
                          sa.Column('lookup_date',
                                    sa.Date,
                                    primary_key=True,
                                    default=func.current_date()
                          ))
