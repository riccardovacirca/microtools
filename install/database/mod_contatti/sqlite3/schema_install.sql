-- Schema installation for mod_contatti (SQLite3)
-- Tabella dei contatti

CREATE TABLE IF NOT EXISTS contatti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    stato VARCHAR(20) DEFAULT 'prospect' CHECK(stato IN ('attivo', 'inattivo', 'prospect', 'cliente', 'lead', 'archiviato')),
    consenso_privacy BOOLEAN DEFAULT 0,
    consenso_marketing BOOLEAN DEFAULT 0,
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

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_contatti_timestamp
AFTER UPDATE ON contatti
FOR EACH ROW
BEGIN
    UPDATE contatti SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Tabella delle liste di contatti
CREATE TABLE IF NOT EXISTS liste_contatti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger per aggiornare updated_at delle liste
CREATE TRIGGER IF NOT EXISTS update_liste_contatti_timestamp
AFTER UPDATE ON liste_contatti
FOR EACH ROW
BEGIN
    UPDATE liste_contatti SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

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
