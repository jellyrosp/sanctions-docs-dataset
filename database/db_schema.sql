CREATE TABLE Actor (
    actor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code     TEXT
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE Categorization (
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
CREATE TABLE Category (
    label       TEXT PRIMARY KEY,
    description TEXT
);
CREATE TABLE Document (
    document_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT,
    official_num TEXT,
    official_url TEXT
);
CREATE TABLE Reason (
    reason_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reason    TEXT    UNIQUE
);
CREATE TABLE Sanction (
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
    REFERENCES "Individual_old" (individual_id) 
);
CREATE TABLE Subscription (
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
CREATE TABLE Individual (
    individual_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    gender TEXT,
    case_study TEXT,
    reason_id INTEGER REFERENCES Reason(reason_id)
);
