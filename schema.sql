DROP TABLE IF EXISTS todos;

CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    completed BOOLEAN NOT NULL,
    date_added DATETIME NOT NULL,
    date_completed DATETIME,
    due_date DATE
);