# DSL Framework Module

Definizione della struttura di un modulo nel framework Microtools.

## Definizione

Un **modulo** è un'unità funzionale autonoma che attraversa tutti i livelli dell'architettura Microtools. Ogni modulo è indipendente, esportabile e importabile.

## Struttura

```
mod_<MODULE_NAME>/
│
├── api/mod_<MODULE_NAME>/           [REQUIRED]  → DSL: python_module.*
│   ├── routes.py                    HTTP routing → DSL: python_module_route.*
│   ├── adapters/                    Un adapter per microservizio → DSL: python_module_adapter.*
│   │   └── <function>_adapter.py
│   ├── services/                    Business logic → DSL: python_module_service.*
│   │   └── <function>_service.py
│   ├── models/                      Validazione Pydantic
│   │   └── <function>_model.py
│   └── repositories/                Accesso DB (opzionale) → DSL: python_module_repository.*
│       └── <function>_repository.py
│
├── gui/src/mod_<MODULE_NAME>/       [OPTIONAL]  → DSL: PROJECT.md (microtools_svelte_gui)
│   ├── index.html                   Entry point sviluppo isolato
│   ├── Layout.svelte                Layout principale
│   └── *Component.svelte            Componenti applicativi
│
├── services/mod_<MODULE_NAME>/      [OPTIONAL]  → DSL: cpp_class.*, PROJECT.md (microtools_cpp_style)
│   ├── CMakeLists.txt               Build configuration
│   ├── src/                         Codice C++
│   ├── include/                     Headers con Doxygen
│   └── .env.example                 Template variabili ambiente
│
└── database/mod_<MODULE_NAME>/      [OPTIONAL]
    ├── sqlite3/
    ├── mariadb/
    ├── postgres/
    ├── *_install.sql
    └── *_uninstall.sql
```

## Relazione Modulo ↔ Microservizi

| Direzione | Cardinalità | Regola |
|-----------|-------------|--------|
| Microservizio → Modulo | **N:1** | Ogni microservizio appartiene a un solo modulo |
| Modulo → Microservizi | **1:N** | Un modulo può contenere più microservizi |

**Regole:**
- Ogni microservizio è esposto tramite un **adapter dedicato**
- I microservizi **non sono mai condivisi** tra moduli
- Se più moduli necessitano funzionalità simili: duplicare il microservizio o implementare logica condivisa a livello API Python

## Flusso Dati

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────────┐
│ Gateway │───▶│   API   │───▶│  Route  │───▶│ Service │───▶│ Adapter │───▶│ Microservice │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └──────────────┘
                                                  │
                                                  ▼
                                            ┌────────────┐    ┌──────────┐
                                            │ Repository │───▶│ Database │
                                            └────────────┘    └──────────┘
```

**Percorsi:**
- **Request**: Gateway → API → Route → Service → Adapter → Microservice
- **Database**: Route → Service → Repository → Database
- **GUI**: GUI → Gateway → API

## Convenzioni Naming

### Nome Modulo
- **Pattern**: `mod_<name>`
- **Stile**: lowercase con underscore
- **Esempi**: `mod_status`, `mod_alerts`, `mod_users`

### Entità API
- **Pattern**: `<function>_<entity>.py`
- **Regola**: Il nome riflette la funzione specifica, non il nome del modulo

| Corretto | Errato |
|----------|--------|
| `info_service.py` | `status_service.py` |
| `alert_adapter.py` | `mod_alerts_adapter.py` |

### Entità GUI
- **Layout**: `Layout.svelte` o `<Name>Layout.svelte`
- **Componenti**: `<Name>Component.svelte`

### Variabili Ambiente Microservizi
- **Pattern**: `MICROSERVICE_MOD_<MODULE_NAME>_<PARAM>`
- **Esempi**: `MICROSERVICE_MOD_STATUS_HOST`, `MICROSERVICE_MOD_STATUS_PORT`

## Configurazione

| File | Scopo |
|------|-------|
| `/workspace/.env` | Configurazione centralizzata |
| `/workspace/services/mod_<NAME>/.env.example` | Template variabili microservizio |

**Prefissi variabili:**
- `MICROSERVICE_` - Microservizi C++
- `API_` - Livello API Python
- `DB_` - Database

## Ciclo di Vita Modulo

### Export
```bash
cmd module export -n <module_name>
```
- Output: `/workspace/dist/modules/<module_name>.tar.gz`
- Include: api, database, gui, services, module.json

### Import
```bash
cmd module import -n <module_name> [--force]
```
- Post-azioni:
  1. Installazione dipendenze Python
  2. Build microservizio C++
  3. Installazione schema database

## Tipi di Modulo

### Modulo Minimo
Solo componente API, senza microservizi, GUI o database.

**Struttura:**
```
api/mod_<MODULE_NAME>/
├── routes.py
└── services/
    └── <function>_service.py
```

**Use case**: Logica Python pura, orchestrazione di altri servizi.

### Modulo Completo
Tutti i componenti: API, GUI, Microservizi, Database.

**Struttura:**
```
api/mod_<MODULE_NAME>/
gui/src/mod_<MODULE_NAME>/
services/mod_<MODULE_NAME>/
database/mod_<MODULE_NAME>/
```

**Use case**: Funzionalità autonoma con frontend, backend, elaborazione C++ e persistenza.

## Pattern Vietati

| Pattern | Motivo |
|---------|--------|
| Microservizi condivisi tra moduli | Viola autonomia del modulo |
| Dipendenze trasversali tra microservizi | Crea accoppiamento |
| Adapter che accedono a microservizi di altri moduli | Viola incapsulamento |
| GUI che chiama direttamente microservizi | Deve passare per API |
| Repository in microservizi C++ | Accesso DB solo via API Python |

## DSL Correlati

Ogni componente del modulo fa riferimento a DSL specifici.

### Componente API

| DSL | File | Descrizione |
|-----|------|-------------|
| Architettura Modulo | `python_module.json` / `.md` | Struttura e convenzioni modulo API |
| Routes | `python_module_route.json` / `.md` | Pattern HTTP routing |
| Services | `python_module_service.json` / `.md` | Business logic e orchestrazione |
| Adapters | `python_module_adapter.json` / `.md` | Interfaccia verso microservizi |
| Repositories | `python_module_repository.json` / `.md` | Accesso database |
| Classi Python | `python_class.json` / `.md` | Stile classi Python |

### Componente GUI

| DSL | Riferimento | Descrizione |
|-----|-------------|-------------|
| Svelte GUI | `PROJECT.md` sezione `microtools_svelte_gui` | Layout e componenti Svelte |

### Componente Microservices

| DSL | File | Descrizione |
|-----|------|-------------|
| Classi C++ | `cpp_class.json` / `.md` | Stile classi C++ |
| Stile C++ | `PROJECT.md` sezione `microtools_cpp_style` | Convenzioni codice C++ |

### Percorso DSL

Tutti i file DSL sono in: `/workspace/.toolchain/prototype/docs/dsl/`
