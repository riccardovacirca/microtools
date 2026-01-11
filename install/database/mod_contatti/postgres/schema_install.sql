-- Schema installation for mod_contatti (PostgreSQL)

-- Crea tipo ENUM per lo stato del contatto
DO $$ BEGIN
    CREATE TYPE stato_contatto AS ENUM (
        'attivo', 'inattivo', 'prospect', 'cliente', 'lead', 'archiviato'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tabella dei contatti
CREATE TABLE IF NOT EXISTS contatti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(50),
    cellulare VARCHAR(50),
    azienda VARCHAR(200),
    ruolo VARCHAR(100),
    indirizzo VARCHAR(500),
    citta VARCHAR(100),
    provincia VARCHAR(2),
    cap VARCHAR(10),
    paese VARCHAR(100) DEFAULT 'Italia',
    stato stato_contatto DEFAULT 'prospect',
    consenso_privacy BOOLEAN DEFAULT FALSE,
    consenso_marketing BOOLEAN DEFAULT FALSE,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_contatti_email ON contatti(email);
CREATE INDEX IF NOT EXISTS idx_contatti_azienda ON contatti(azienda);
CREATE INDEX IF NOT EXISTS idx_contatti_stato ON contatti(stato);
CREATE INDEX IF NOT EXISTS idx_contatti_deleted_at ON contatti(deleted_at);
CREATE INDEX IF NOT EXISTS idx_contatti_nome_cognome ON contatti(nome, cognome);

-- Trigger function per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_contatti_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare updated_at
DROP TRIGGER IF EXISTS trigger_update_contatti_timestamp ON contatti;
CREATE TRIGGER trigger_update_contatti_timestamp
BEFORE UPDATE ON contatti
FOR EACH ROW
EXECUTE FUNCTION update_contatti_timestamp();

-- Tabella delle liste di contatti
CREATE TABLE IF NOT EXISTS liste_contatti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger function per aggiornare updated_at delle liste
CREATE OR REPLACE FUNCTION update_liste_contatti_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare updated_at delle liste
DROP TRIGGER IF EXISTS trigger_update_liste_contatti_timestamp ON liste_contatti;
CREATE TRIGGER trigger_update_liste_contatti_timestamp
BEFORE UPDATE ON liste_contatti
FOR EACH ROW
EXECUTE FUNCTION update_liste_contatti_timestamp();

-- Tabella di join many-to-many tra contatti e liste
CREATE TABLE IF NOT EXISTS contatto_lista (
    contatto_id INTEGER NOT NULL,
    lista_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contatto_id, lista_id),
    FOREIGN KEY (contatto_id) REFERENCES contatti(id) ON DELETE CASCADE,
    FOREIGN KEY (lista_id) REFERENCES liste_contatti(id) ON DELETE CASCADE
);

-- Indici per la tabella di join
CREATE INDEX IF NOT EXISTS idx_contatto_lista_contatto ON contatto_lista(contatto_id);
CREATE INDEX IF NOT EXISTS idx_contatto_lista_lista ON contatto_lista(lista_id);
