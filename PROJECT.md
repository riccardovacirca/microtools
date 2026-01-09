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

- project: Cartella relativa al progetto originale git
- install: Link simbolico alla cartella di installazione del framework
- install.sh e setup.sh: Link simbolici agli script di installazione del framework

La root del progetto e la cartella project hanno un repository .git individuale
per gestire gli aggiornamenti a livello del framework (che vengono condivisi tra
tutte le installazioni) e gli aggiornamenti a livello della singola istanza del
progetto.

## Gestione del progetto

La gestione di un progetto applicativo con Microtools avviene mediante l'uso
dello script sh bin/wa. Questo script può essere utilizzato per:

- Start/Stop/Restart di un servizio di sistema o di un microservizio
- Build di un microservizio C++ o del frontend Vite/Svelte
- Verifica/Monitoraggio dello stato di un servizio di sistema o di un microservizio
- Installazione di un modulo SQL di database
- Sincronizzazione dei repository git della webapp e del framework

