CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS chats (
 id SERIAL PRIMARY KEY,
 telegram_id INT UNIQUE NOT NULL,
 chat_type VARCHAR(50),
 username VARCHAR(200),
 first_name VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS notes (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      chat_id INT NOT NULL REFERENCES chats(telegram_id),
      note_text TEXT NOT NULL,
      note_time TIMESTAMP,
      created TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sermons (
      id SERIAL PRIMARY KEY,
      sermon_text TEXT NOT NULL,
      title VARCHAR(200),
      sutta VARCHAR(200),
      meta_info VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS currency_rates (
       rates JSON NOT NULL,
       lookup_date Date NOT NULL,
       base varchar(10) NOT NULL,
       primary key(lookup_date, base)
);


CREATE INDEX ON notes(chat_id);
CREATE INDEX ON notes(note_time);
CREATE INDEX ON chats(telegram_id);
