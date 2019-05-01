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

CREATE TABLE IF NOT EXISTS cermons (
      id SERIAL PRIMARY KEY,
      cermon_text TEXT NOT NULL,
      title VARCHAR(200),
      sutta VARCHAR(200),
      meta_info VARCHAR(200)
);


CREATE INDEX ON notes(chat_id);
CREATE INDEX ON notes(note_time);
CREATE INDEX ON chats(telegram_id);
