-- Initial data for mod_status app_status table
-- Insert application name and version

INSERT INTO app_status (id, version)
VALUES (1, '1.0.0')
ON DUPLICATE KEY UPDATE version = VALUES(version);
