-- Sample data for mod_contatti (MariaDB)

-- Inserisci liste di esempio
INSERT INTO liste_contatti (nome, descrizione) VALUES
    ('Clienti VIP', 'Clienti di alto valore'),
    ('Newsletter', 'Iscritti alla newsletter'),
    ('Lead Qualificati', 'Lead pronti per il contatto commerciale'),
    ('Partner', 'Partner commerciali');

-- Inserisci contatti di esempio
INSERT INTO contatti (
    nome, cognome, email, telefono, cellulare, azienda, ruolo,
    citta, provincia, stato, consenso_privacy, consenso_marketing
) VALUES
    ('Mario', 'Rossi', 'mario.rossi@example.com', '02 1234567', '+39 333 1234567',
     'Acme Corp', 'CEO', 'Milano', 'MI', 'cliente', TRUE, TRUE),

    ('Laura', 'Bianchi', 'laura.bianchi@example.com', NULL, '+39 345 7654321',
     'Tech Solutions', 'CTO', 'Roma', 'RM', 'prospect', TRUE, FALSE),

    ('Giuseppe', 'Verdi', 'g.verdi@example.com', '011 9876543', NULL,
     'Innovate SRL', 'Marketing Manager', 'Torino', 'TO', 'lead', TRUE, TRUE),

    ('Anna', 'Neri', 'anna.neri@example.com', NULL, '+39 320 1112233',
     NULL, 'Freelance Developer', 'Napoli', 'NA', 'attivo', TRUE, TRUE);

-- Assegna contatti alle liste
INSERT INTO contatto_lista (contatto_id, lista_id) VALUES
    (1, 1), -- Mario Rossi -> Clienti VIP
    (1, 2), -- Mario Rossi -> Newsletter
    (2, 3), -- Laura Bianchi -> Lead Qualificati
    (3, 2), -- Giuseppe Verdi -> Newsletter
    (3, 3), -- Giuseppe Verdi -> Lead Qualificati
    (4, 2); -- Anna Neri -> Newsletter
