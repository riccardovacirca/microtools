-- Schema uninstallation for mod_contatti (MariaDB)

-- Drop tables (in reverse order to respect foreign keys)
DROP TABLE IF EXISTS contatto_lista;
DROP TABLE IF EXISTS liste_contatti;
DROP TABLE IF EXISTS contatti;
