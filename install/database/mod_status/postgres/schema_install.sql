-- mod_status database schema for PostgreSQL
-- Simple table to verify database connectivity

-- Application information table
CREATE TABLE IF NOT EXISTS app_status (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_app_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
DROP TRIGGER IF EXISTS update_app_status_timestamp_trigger ON app_status;
CREATE TRIGGER update_app_status_timestamp_trigger
BEFORE UPDATE ON app_status
FOR EACH ROW
EXECUTE FUNCTION update_app_status_timestamp();
