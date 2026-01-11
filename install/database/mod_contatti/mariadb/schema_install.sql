-- Schema installation for mod_contatti (MariaDB)
-- Tabella dei contatti

CREATE TABLE IF NOT EXISTS contatti (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    stato ENUM('attivo', 'inattivo', 'prospect', 'cliente', 'lead', 'archiviato') DEFAULT 'prospect',
    consenso_privacy BOOLEAN DEFAULT FALSE,
    consenso_marketing BOOLEAN DEFAULT FALSE,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_azienda (azienda),
    INDEX idx_stato (stato),
    INDEX idx_deleted_at (deleted_at),
    INDEX idx_nome_cognome (nome, cognome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabella delle liste di contatti
CREATE TABLE IF NOT EXISTS liste_contatti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descrizione TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabella di join many-to-many tra contatti e liste
CREATE TABLE IF NOT EXISTS contatto_lista (
    contatto_id INT NOT NULL,
    lista_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contatto_id, lista_id),
    FOREIGN KEY (contatto_id) REFERENCES contatti(id) ON DELETE CASCADE,
    FOREIGN KEY (lista_id) REFERENCES liste_contatti(id) ON DELETE CASCADE,
    INDEX idx_contatto (contatto_id),
    INDEX idx_lista (lista_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
