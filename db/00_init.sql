CREATE USER tgbot WITH PASSWORD '1234567890';
CREATE TABLE emails(
   id SERIAL PRIMARY KEY,
   email VARCHAR(255) NOT NULL,
   insert_time TIMESTAMP NULL
);


CREATE TABLE phone_numbers(
   id SERIAL PRIMARY KEY,
   phone VARCHAR(255) NOT NULL,
   insert_time TIMESTAMP NULL
);

CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'replication123';
SELECT pg_create_physical_replication_slot('replication_slot');

GRANT SELECT, INSERT, UPDATE, TRIGGER ON  emails TO tgbot;
GRANT SELECT, INSERT, UPDATE, TRIGGER ON  phone_numbers TO tgbot;
GRANT ALL ON SEQUENCE emails_id_seq to tgbot;
GRANT ALL ON SEQUENCE phone_numbers_id_seq to tgbot;

