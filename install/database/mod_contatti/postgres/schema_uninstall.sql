-- Schema uninstallation for mod_contatti (PostgreSQL)

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_contatti_timestamp ON contatti;
DROP TRIGGER IF EXISTS trigger_update_liste_contatti_timestamp ON liste_contatti;

-- Drop trigger functions
DROP FUNCTION IF EXISTS update_contatti_timestamp();
DROP FUNCTION IF EXISTS update_liste_contatti_timestamp();

-- Drop tables (in reverse order to respect foreign keys)
DROP TABLE IF EXISTS contatto_lista;
DROP TABLE IF EXISTS liste_contatti;
DROP TABLE IF EXISTS contatti;

-- Drop enum type
DROP TYPE IF EXISTS stato_contatto;
