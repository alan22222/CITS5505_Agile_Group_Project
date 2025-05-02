-- Creating user table
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);

-- Creating UploadedData table
CREATE TABLE UploadedData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(120) NOT NULL,
    user_id INTEGER NOT NULL,
    graph_path VARCHAR(200),
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

-- Creating ModelRun table
CREATE TABLE ModelRun (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    model_type VARCHAR(50),
    precision_mode VARCHAR(20),
    target_index INTEGER,
    has_header BOOLEAN,
    result_json TEXT,
    graph_path VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);
-- Creating SharedFiles table
CREATE TABLE SharedFiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    current_uid INTEGER NOT NULL,
    target_uid INTEGER NOT NULL,
    result_id INTEGER NOT NULL,
    FOREIGN KEY (current_uid) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (target_uid) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (result_id) REFERENCES ModelRun(id) ON DELETE CASCADE
);
