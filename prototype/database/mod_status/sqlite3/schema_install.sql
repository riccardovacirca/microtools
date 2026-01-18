-- mod_status database schema for SQLite3
-- Simple table to verify database connectivity

-- Application information table
CREATE TABLE IF NOT EXISTS app_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_app_status_timestamp
AFTER UPDATE ON app_status
BEGIN
    UPDATE app_status SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
