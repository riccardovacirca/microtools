-- Schema uninstallation for mod_contatti (SQLite3)

-- Drop triggers
DROP TRIGGER IF EXISTS update_contatti_timestamp;
DROP TRIGGER IF EXISTS update_liste_contatti_timestamp;

-- Drop tables (in reverse order to respect foreign keys)
DROP TABLE IF EXISTS contatto_lista;
DROP TABLE IF EXISTS liste_contatti;
DROP TABLE IF EXISTS contatti;
