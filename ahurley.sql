DROP TABLE IF EXISTS public.journal;
DROP TABLE IF EXISTS public.rooms;

CREATE TABLE public.rooms (
    id SERIAL PRIMARY KEY,
    name character varying NOT NULL UNIQUE,
    count integer NOT NULL DEFAULT 0
);

CREATE TABLE public.journal (
    id SERIAL PRIMARY KEY,
    room_id integer NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    previous_count integer DEFAULT 0,
    count integer NOT NULL DEFAULT 0,
    delta integer GENERATED ALWAYS AS (count - COALESCE(previous_count, 0)) STORED,
    applied_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_journal_record() RETURNS trigger AS $journal_stamp$
    BEGIN
        INSERT INTO public.JOURNAL (room_id, previous_count, count) VALUES (NEW.id, OLD.count, NEW.count);

        IF NEW.count IS NULL THEN
            RAISE EXCEPTION 'count cannot be null';
        END IF;

        IF NEW.count < 0 THEN
            RAISE EXCEPTION '% cannot have a negative count', NEW.id;
        END IF;

        RETURN NEW;
    END;
$journal_stamp$ LANGUAGE plpgsql;

CREATE TRIGGER update_journal
    AFTER UPDATE OR INSERT ON public.rooms
    FOR EACH ROW
    EXECUTE PROCEDURE update_journal_record();

INSERT INTO rooms (name) VALUES ('kitchen');
INSERT INTO rooms (name) VALUES ('office');
INSERT INTO rooms (name) VALUES ('garage');


