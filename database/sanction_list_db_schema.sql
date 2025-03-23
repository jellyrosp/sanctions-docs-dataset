--
-- File generated with SQLiteStudio v3.4.17 on Sun Mar 23 19:45:47 2025
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Actor
CREATE TABLE IF NOT EXISTS Actor (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code     TEXT
);


-- Table: Categorization
CREATE TABLE IF NOT EXISTS Categorization (
    reason_id INTEGER,
    label     TEXT,
    FOREIGN KEY (
        label
    )
    REFERENCES Category (label),
    FOREIGN KEY (
        reason_id
    )
    REFERENCES Reason (reason_id) 
);


-- Table: Category
CREATE TABLE IF NOT EXISTS Category (
    label       TEXT PRIMARY KEY,
    description TEXT
);


-- Table: Document
CREATE TABLE IF NOT EXISTS Document (
    document_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT,
    official_num TEXT,
    official_url TEXT
);


-- Table: Individual
CREATE TABLE IF NOT EXISTS Individual (
    individual_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT,
    gender        TEXT,
    nationality   TEXT,
    reason_id        TEXT,
    FOREIGN KEY (
        reason_id
    )
    REFERENCES Categorization (reason_id) 
);


-- Table: Reason
CREATE TABLE IF NOT EXISTS Reason (
    reason_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reason    TEXT    UNIQUE
);


-- Table: Sanction
CREATE TABLE IF NOT EXISTS Sanction (
    document_id   INTEGER,
    individual_id INTEGER,
    start_date    TEXT,
    FOREIGN KEY (
        document_id
    )
    REFERENCES Document (document_id),
    FOREIGN KEY (
        individual_id
    )
    REFERENCES Individual (individual_id) 
);


-- Table: Subscription
CREATE TABLE IF NOT EXISTS Subscription (
    document_id INTEGER,
    actor_id    INTEGER,
    FOREIGN KEY (
        document_id
    )
    REFERENCES Document (document_id),
    FOREIGN KEY (
        actor_id
    )
    REFERENCES Actor (actor_id) 
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
