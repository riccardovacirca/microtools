# Modulo Contatti - CRM

## Descrizione

Il modulo `mod_contatti` fornisce un sistema completo di gestione contatti per applicazioni CRM (Customer Relationship Management). Permette di memorizzare, organizzare e gestire informazioni anagrafiche e di contatto con supporto per soft delete, stati personalizzati e consensi privacy/marketing.

## Funzionalità Principali

### Gestione Contatti

- **CRUD Completo**: Creazione, lettura, aggiornamento ed eliminazione contatti
- **Dati Anagrafici**: Nome, cognome, email, telefoni, indirizzo completo
- **Informazioni Aziendali**: Azienda, ruolo professionale
- **Stati Personalizzati**: attivo, inattivo, prospect, cliente, lead, archiviato
- **Consensi**: Privacy e marketing (GDPR compliant)
- **Note**: Campo testo libero per annotazioni

### Liste di Contatti

- Organizzazione in liste multiple
- Relazione many-to-many contatto-lista
- Ogni contatto può appartenere a più liste
- Gestione CRUD delle liste

### Soft Delete e Hard Delete

- **Soft Delete**: Archiviazione contatti (campo `deleted_at`)
- **Hard Delete**: Eliminazione permanente dal database
- **Ripristino**: Recupero contatti archiviati
- Filtro per visualizzare contatti archiviati

### Ricerca e Paginazione

- Ricerca full-text su nome, cognome, email, azienda
- Paginazione configurabile
- Ordinamento per data di creazione

## Architettura

### API Layer (Python/FastAPI)

**Models** (Pydantic):
- `ContattoCreate`: Validazione dati per creazione
- `ContattoUpdate`: Validazione dati per aggiornamento (campi opzionali)
- `ContattoResponse`: Risposta con dati completi
- `ContattoList`: Lista paginata
- `ListaContattiCreate/Response`: Gestione liste

**Repository**:
- `ContattiRepository`: Accesso dati tramite ODBC
- `ListeContattiRepository`: Gestione liste
- Query parametrizzate per sicurezza

**Service**:
- `ContattiService`: Business logic
- Validazione dati
- Gestione transazioni

**Routes**:
- `GET /api/contatti`: Lista contatti paginata
- `GET /api/contatti/search`: Ricerca contatti
- `GET /api/contatti/{id}`: Dettaglio contatto
- `POST /api/contatti`: Crea contatto
- `PUT /api/contatti/{id}`: Aggiorna contatto
- `DELETE /api/contatti/{id}/soft`: Soft delete
- `DELETE /api/contatti/{id}/hard`: Hard delete
- `POST /api/contatti/{id}/restore`: Ripristina contatto
- `GET/POST/DELETE /api/contatti/liste`: Gestione liste

### Database Layer (SQL)

**Tabelle**:

1. **contatti**: Tabella principale
   - Dati anagrafici completi
   - Stati e consensi
   - Timestamp: created_at, updated_at, deleted_at
   - Indici su email, azienda, stato, nome/cognome

2. **liste_contatti**: Liste di organizzazione
   - nome (unique)
   - descrizione
   - Timestamp automatici

3. **contatto_lista**: Join table many-to-many
   - Foreign keys con CASCADE DELETE
   - Indici su entrambe le chiavi

**Supporto Multi-Database**:
- SQLite3 (development, small deployments)
- MariaDB (production)
- PostgreSQL (production, advanced features)

### GUI Layer (Svelte)

**Componenti**:

1. **Layout.svelte**: Entry point del modulo
2. **ContattiList.svelte**: Lista principale con paginazione e ricerca
3. **ContattoCard.svelte**: Card per visualizzazione singolo contatto
4. **ContattoForm.svelte**: Form modale per crea/modifica

**Features GUI**:
- Ricerca in tempo reale
- Paginazione
- Filtro contatti archiviati
- Form validato con tutti i campi
- Gestione liste con checkbox
- Azioni soft/hard delete
- Ripristino contatti
- Design responsive

## Installazione

### 1. Database

Scegli il database appropriato e installa lo schema:

```bash
# SQLite3 (default)
mt db -f /workspace/database/mod_contatti/sqlite3_install.sql

# MariaDB
mt db -f /workspace/database/mod_contatti/mariadb_install.sql

# PostgreSQL
mt db -f /workspace/database/mod_contatti/postgres_install.sql
```

### 2. Registrazione Router

Aggiungi il router FastAPI in `/workspace/api/main.py`:

```python
from mod_contatti import router as contatti_router

app.include_router(contatti_router)
```

### 3. GUI

Il modulo GUI è già disponibile in `/workspace/gui/src/mod_contatti/`.

Per includere il modulo nella navigazione principale, modifica `/workspace/gui/src/Layout.svelte` aggiungendo un link al modulo contatti.

## Utilizzo

### Esempi API

#### Creare un contatto

```bash
curl -X POST http://localhost:2310/api/contatti \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Mario",
    "cognome": "Rossi",
    "email": "mario.rossi@example.com",
    "telefono": "+39 02 1234567",
    "azienda": "Acme Corp",
    "stato": "cliente",
    "consenso_privacy": true,
    "liste_ids": [1, 2]
  }'
```

#### Cercare contatti

```bash
curl "http://localhost:2310/api/contatti/search?q=mario&page=1&page_size=20"
```

#### Archiviare un contatto

```bash
curl -X DELETE http://localhost:2310/api/contatti/1/soft
```

#### Eliminare permanentemente

```bash
curl -X DELETE http://localhost:2310/api/contatti/1/hard
```

## Stati dei Contatti

- **attivo**: Contatto attivo nella base dati
- **inattivo**: Contatto temporaneamente non attivo
- **prospect**: Potenziale cliente
- **cliente**: Cliente acquisito
- **lead**: Lead commerciale da seguire
- **archiviato**: Contatto archiviato

## Consensi GDPR

Il modulo supporta la gestione dei consensi per conformità GDPR:

- **consenso_privacy**: Consenso trattamento dati personali (obbligatorio)
- **consenso_marketing**: Consenso invio comunicazioni marketing (opzionale)

Entrambi i consensi sono tracciati a livello di database e possono essere modificati in qualsiasi momento.

## Note di Sviluppo

- I repository utilizzano ODBC per la connessione al database
- Le query sono parametrizzate per prevenire SQL injection
- Il soft delete mantiene i dati per audit e recupero
- Gli indici sono ottimizzati per query frequenti (ricerca, filtri)
- Le liste usano relazioni many-to-many con CASCADE DELETE

## Estensioni Future

Possibili estensioni del modulo:

- Import/export CSV
- Integrazione con servizi email
- Storia delle modifiche (audit log)
- Campi personalizzati
- Segmentazione avanzata
- Integrazione con campagne marketing
- API per sincronizzazione con sistemi esterni
