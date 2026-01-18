-- mod_status database schema uninstall for SQLite3
-- Removes all objects created by schema_install.sql

-- Drop trigger first (depends on table)
DROP TRIGGER IF EXISTS update_app_status_timestamp;

-- Drop table
DROP TABLE IF EXISTS app_status;
