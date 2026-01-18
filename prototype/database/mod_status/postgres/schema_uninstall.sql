-- mod_status database schema uninstall for PostgreSQL
-- Removes all objects created by schema_install.sql

-- Drop trigger first (depends on table and function)
DROP TRIGGER IF EXISTS update_app_status_timestamp_trigger ON app_status;

-- Drop function (depends on nothing)
DROP FUNCTION IF EXISTS update_app_status_timestamp();

-- Drop table
DROP TABLE IF EXISTS app_status;
