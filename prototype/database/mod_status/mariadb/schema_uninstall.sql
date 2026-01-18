-- mod_status database schema uninstall for MariaDB/MySQL
-- Removes all objects created by schema_install.sql

-- Drop table (trigger is auto-managed by MariaDB via ON UPDATE CURRENT_TIMESTAMP)
DROP TABLE IF EXISTS app_status;
