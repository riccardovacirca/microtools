# Microtools

Microtools è un framework per lo sviluppo di applicazioni modulari basate su
una architettura a 5 livelli: Gateway, GUI, API , Microservice, Database.
Il Gateway e implementato mediante Nginx, la GUI è implementata in Vite/Svelte,
la API in python/FastAPI (Uvicorn/Gunicorn), i Microservice in C++ e il
database supporta i server SQLite3, MariaDB, PostgreSQL a cui si aggiunge il
server Redis.

Il livello Gateway (Nginx) riceve le richieste dai client HTTP e le inoltra al
livello API.

Il livello API è organizzato in moduli Python che implementano una
logica basata su cinque entità applicative: Router, Model, Service, Adapter e
Repository. Il Router implementa il routing delle richieste, i Model la
validazione dei parametri della richiesta mediante Pydantic, i Service
implementano la logica applicativa del modulo, i Repository definiscono la
connessione con il database e gli Adapter implementano una interfaccia con il
livello dei Microservice.

Un modulo del livello API può gestire direttamente la richiesta del client
oppure proxarla mediante un Adapter a un Microservice.

I Microservice sono sviluppati in C++ e sono in esecuzione per tutto il ciclo di
vita dell'applicazione. L'ambiente di sviluppo dei Microservice è basato sul
compilatore gcc e utilizza Cmake. Il framework comprende una libreria di
supporto per lo sviluppo dei Microservice nella cartella lib. Lo scopo di questa
libreria è anche quello di basare lo sviluppo dei Microservice su una logica
comune e semplificata. L'organizzazione del codice dei componenti della libreria
è basata su un DSL che definisce un insieme di vincoli sintattici che enfatizzano
chiarezza e semplicità.

Il sistema è containerizzato e lo stato dei servizzi è gestito mediante S6 il
cui scopo è garantire persistenza in caso di riavvio del container.

## Organizzazione di file e cartelle

Un progetto applicativo basato su Microtools ha la seguente struttura:

- bin: Cartella degli script Bash di gestione del progetto
- logs: Cartella dei logs
- conf: Cartella dei file di configurazione dei servizi
- api: Cartella dei moduli Python che espongono l'API del progetto
- data: Cartella dati. Può contenere il database SQLite3
- database: Cartella dei moduli SQL del progetto
- gui: Cartella dei moduli del frontend Vite/Svelte
- services: Cartella dei Microservice del progetto
- .env: File di configurazione centralizzato

A questi si aggiungono:

- .prototype: Cartella relativa al progetto originale git
- install: Link simbolico alla cartella di installazione del framework
- install.sh e setup.sh: Link simbolici agli script di installazione del framework

La root del progetto e la cartella .prototype hanno un repository .git individuale
per gestire gli aggiornamenti a livello del framework (che vengono condivisi tra
tutte le installazioni) e gli aggiornamenti a livello della singola istanza del
progetto.

## Gestione del progetto

La gestione di un progetto applicativo con Microtools avviene mediante l'uso
dello script sh bin/mt. Questo script può essere utilizzato per:

- Start/Stop/Restart di un servizio di sistema o di un microservizio
- Build di un microservizio C++ o del frontend Vite/Svelte
- Verifica/Monitoraggio dello stato di un servizio di sistema o di un microservizio
- Installazione di un modulo SQL di database
- Sincronizzazione dei repository git della webapp e del framework

# Struttura di un modulo

Il modulo mod_status è un esempio di come i file e le cartelle di un modulo sono 
organizzate nel progetto.

Il livello più alto è rappresentato dalla API Python che fornisce il routing e
la validazione dell'input. I componenti database, gui, services sono opzionali.

/workspace/api/mod_status
|-- /workspace/api/mod_status/__init__.py
|-- /workspace/api/mod_status/adapters
|   |-- /workspace/api/mod_status/adapters/__init__.py
|   `-- /workspace/api/mod_status/adapters/cpp_adapter.py
|-- /workspace/api/mod_status/models
|   |-- /workspace/api/mod_status/models/__init__.py
|   `-- /workspace/api/mod_status/models/response_models.py
|-- /workspace/api/mod_status/repositories
|   `-- /workspace/api/mod_status/repositories/__init__.py
|-- /workspace/api/mod_status/routes.py
|-- /workspace/api/mod_status/services
|   |-- /workspace/api/mod_status/services/__init__.py
|   `-- /workspace/api/mod_status/services/status_service.py
`-- /workspace/api/mod_status/workflow.md

/workspace/database/mod_status
|-- /workspace/database/mod_status/mariadb
|   |-- /workspace/database/mod_status/mariadb/data.sql
|   |-- /workspace/database/mod_status/mariadb/schema_install.sql
|   `-- /workspace/database/mod_status/mariadb/schema_uninstall.sql
|-- /workspace/database/mod_status/mariadb_install.sql
|-- /workspace/database/mod_status/mariadb_uninstall.sql
|-- /workspace/database/mod_status/postgres
|   |-- /workspace/database/mod_status/postgres/data.sql
|   |-- /workspace/database/mod_status/postgres/schema_install.sql
|   `-- /workspace/database/mod_status/postgres/schema_uninstall.sql
|-- /workspace/database/mod_status/postgres_install.sql
|-- /workspace/database/mod_status/postgres_uninstall.sql
|-- /workspace/database/mod_status/sqlite3
|   |-- /workspace/database/mod_status/sqlite3/data.sql
|   |-- /workspace/database/mod_status/sqlite3/schema_install.sql
|   `-- /workspace/database/mod_status/sqlite3/schema_uninstall.sql
|-- /workspace/database/mod_status/sqlite3_install.sql
`-- /workspace/database/mod_status/sqlite3_uninstall.sql

/workspace/gui/src/mod_status
|-- /workspace/gui/src/mod_status/Info.svelte
|-- /workspace/gui/src/mod_status/Layout.svelte
`-- /workspace/gui/src/mod_status/index.html

/workspace/services/mod_status
|-- /workspace/services/mod_status/.env.example
|-- /workspace/services/mod_status/CMakeLists.txt
`-- /workspace/services/mod_status/src
    `-- /workspace/services/mod_status/src/main.cpp