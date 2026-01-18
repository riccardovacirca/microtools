# DSL Database Module

Definizione della struttura dei file SQL per un modulo database nel framework Microtools.

## Struttura Directory

```
/workspace/database/mod_<MODULE_NAME>/
├── sqlite3/
│   ├── schema_install.sql    # CREATE TABLE, CREATE INDEX
│   ├── schema_uninstall.sql  # DROP TABLE
│   └── data.sql              # INSERT (opzionale)
├── sqlite3_install.sql       # Entry point install
├── sqlite3_uninstall.sql     # Entry point uninstall
├── mariadb/
│   ├── schema_install.sql
│   ├── schema_uninstall.sql
│   └── data.sql
├── mariadb_install.sql
├── mariadb_uninstall.sql
├── postgres/
│   ├── schema_install.sql
│   ├── schema_uninstall.sql
│   └── data.sql
├── postgres_install.sql
└── postgres_uninstall.sql
```

## Direttiva @require

La direttiva `-- @require` specifica dipendenze tra file SQL ed è gestita da `bin/cmd`.

SYNTAX:
```sql
-- @require <relative_path>
```

PROCESSING:
  - bin/cmd analizza le direttive @require
  - Determina l'ordine di esecuzione dei file
  - Path relativo alla directory del modulo database

EXAMPLES:
```sql
-- @require sqlite3/schema_install.sql
-- @require sqlite3/data.sql
```

## File Entry Point

I file entry point (`<dbtype>_install.sql`, `<dbtype>_uninstall.sql`) contengono SOLO direttive @require.

### Install Entry Point

FILE: `sqlite3_install.sql`
```sql
-- @require sqlite3/schema_install.sql
-- @require sqlite3/data.sql
```

### Uninstall Entry Point

FILE: `sqlite3_uninstall.sql`
```sql
-- @require sqlite3/schema_uninstall.sql
```

## File Schema

### schema_install.sql

LOCATION: `<dbtype>/schema_install.sql`
CONTENT: CREATE TABLE, CREATE INDEX, constraint definitions
ORDER: Tabelle senza dipendenze prima, poi tabelle con foreign key

EXAMPLE:
```sql
-- Schema mod_risorse per SQLite3

CREATE TABLE IF NOT EXISTS contatti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    ...
);

CREATE INDEX IF NOT EXISTS idx_contatti_email ON contatti(email);

-- Tabelle con foreign key dopo
CREATE TABLE IF NOT EXISTS lista_contatti (
    lista_id INTEGER NOT NULL,
    contatto_id INTEGER NOT NULL,
    PRIMARY KEY (lista_id, contatto_id),
    FOREIGN KEY (lista_id) REFERENCES liste(id) ON DELETE CASCADE,
    FOREIGN KEY (contatto_id) REFERENCES contatti(id) ON DELETE CASCADE
);
```

### schema_uninstall.sql

LOCATION: `<dbtype>/schema_uninstall.sql`
CONTENT: DROP TABLE statements
ORDER: Ordine inverso rispetto a schema_install (tabelle dipendenti prima)

EXAMPLE:
```sql
-- Rimozione schema mod_risorse per SQLite3

-- Prima le tabelle con foreign key
DROP TABLE IF EXISTS campagna_liste;
DROP TABLE IF EXISTS lista_contatti;

-- Poi le tabelle principali
DROP TABLE IF EXISTS campagne;
DROP TABLE IF EXISTS liste;
DROP TABLE IF EXISTS contatti;
```

### data.sql

LOCATION: `<dbtype>/data.sql`
CONTENT: INSERT statements per dati iniziali
OPTIONAL: Sì, può essere vuoto o contenere solo commenti

EXAMPLE:
```sql
-- Dati iniziali mod_risorse per SQLite3
-- (vuoto o INSERT statements)
```

## Naming Conventions

| Elemento | Pattern |
|----------|---------|
| Directory modulo | `mod_<MODULE_NAME>` |
| Directory dbtype | `sqlite3`, `mariadb`, `postgres` |
| Entry point install | `<dbtype>_install.sql` |
| Entry point uninstall | `<dbtype>_uninstall.sql` |
| Schema install | `<dbtype>/schema_install.sql` |
| Schema uninstall | `<dbtype>/schema_uninstall.sql` |
| Dati | `<dbtype>/data.sql` |

## Pattern Vietati

| Pattern | Motivo | Alternativa |
|---------|--------|-------------|
| `.read`, `.import` | Comandi SQLite-specifici non portabili | `-- @require` |
| Commenti descrittivi in entry point | Entry point solo per @require | Commenti in schema files |
| SQL in entry point | Entry point delega a schema files | Mettere SQL in `<dbtype>/` |

## Esecuzione

INSTALL:
```bash
cmd db install -m <module_name> -t <dbtype>
```

UNINSTALL:
```bash
cmd db uninstall -m <module_name> -t <dbtype>
```

PROCESSING:
1. bin/cmd legge il file entry point
2. Analizza le direttive `-- @require`
3. Risolve le dipendenze e determina l'ordine
4. Esegue i file SQL nell'ordine corretto

## Esempio Completo

MODULE: mod_risorse

```
/workspace/database/mod_risorse/
├── sqlite3/
│   ├── schema_install.sql
│   ├── schema_uninstall.sql
│   └── data.sql
├── sqlite3_install.sql       # -- @require sqlite3/schema_install.sql
│                             # -- @require sqlite3/data.sql
└── sqlite3_uninstall.sql     # -- @require sqlite3/schema_uninstall.sql
```
