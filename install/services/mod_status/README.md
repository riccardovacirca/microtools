# mod_status Example - MicroTools DSL Demo

Versione semplificata del microservizio `mod_status` che dimostra l'utilizzo della libreria **MicroTools DSL**.

## Descrizione

Questo esempio mostra come utilizzare le classi MicroTools per creare un microservizio HTTP:

- **Env** - Lettura variabili ambiente per configurazione
- **Record** - Gestione dati chiave/valore
- **RecordSet** - Collezioni di record con filtering
- **JSON** - Serializzazione JSON
- **File** - Operazioni su file

## Differenze rispetto all'originale

### Originale (`/project/install/services/mod_status`)
- Usa direttamente httplib, nlohmann/json, e funzioni C++ standard
- Include system_info.h, database.h con logica complessa
- ~200 righe di codice distribuito in 6+ file
- Dipendenze: httplib, nlohmann/json, SQLite/MySQL/PostgreSQL

### Versione semplificata (questo esempio)
- Usa la libreria **MicroTools DSL** per astrazione
- Singolo file main.cpp (~76 righe)
- Dimostra Env e Record
- Dipendenze: httplib + **microtools**

## Struttura

```
mod_status/
├── CMakeLists.txt       # Build configuration
├── README.md            # Questo file
└── src/
    └── main.cpp         # Microservizio semplificato con MicroTools
```

## Compilazione

### 1. Compilare prima la libreria microtools

```bash
cd /workspace/project/install/lib/microtools
mkdir -p build && cd build
cmake ..
make
```

### 2. Compilare l'esempio

```bash
cd /workspace/project/install/examples/mod_status
mkdir -p build && cd build
cmake ..
make
```

Il binario verrà creato in `bin/mod_status_example`.

## Esecuzione

```bash
# Impostare le variabili ambiente (opzionale)
export MOD_STATUS_HOST=127.0.0.1
export MOD_STATUS_PORT=9001
export PROJECT_NAME=microtools-demo
export VERSION=1.0.0

# Eseguire il servizio
./bin/mod_status_example
```

## Endpoint disponibile

### GET /api/info - Project Info
```bash
curl http://127.0.0.1:9001/api/info
```
**Output**:
```json
{"project":"microtools-demo","version":"1.0.0"}
```
**MicroTools usate**: `Env`, `Record`

## Codice dell'esempio

Il servizio è estremamente semplice e dimostra l'uso di:

### 1. Env - Lettura variabili ambiente
```cpp
Env env;
auto projectNamePtr = env.get("PROJECT_NAME");
std::string projectName = projectNamePtr ? *projectNamePtr : "webapp";
// No delete needed - automatic cleanup with unique_ptr!
```

### 2. Record - Costruzione risposta JSON
```cpp
Record record;
record.set("project", projectName);
record.set("version", version);
std::string jsonResponse = record.toString(Format::JSON);
// Output: {"project":"microtools-demo","version":"1.0.0"}
```

### 3. Logger - Logging su file con spdlog
```cpp
// Initialize logger at startup
logger = std::make_unique<Logger>("mod_status", "/workspace/logs/mod_status.log");
logger->info("Service starting...");

// Log in request handler
server.set_logger([](const httplib::Request& req, const httplib::Response& res) {
  std::string logMessage = "[" + req.method + "] " + req.path + " - " + std::to_string(res.status);

  if (res.status >= 500) {
    logger->error(logMessage);  // Errors in red
  } else if (res.status >= 400) {
    logger->warn(logMessage);   // Warnings in yellow
  } else {
    logger->info(logMessage);   // Info in white
  }
});
```

**Log file**: `/workspace/logs/mod_status.log`

**Formato log**:
```
[2026-01-05 09:35:42.123] [info] Service starting...
[2026-01-05 09:35:42.456] [info] Configuration loaded - Host: 127.0.0.1, Port: 9001
[2026-01-05 09:35:42.789] [info] Server listening on 127.0.0.1:9001
[2026-01-05 09:36:15.234] [info] [GET] /api/info - 200
[2026-01-05 09:36:20.567] [warn] [GET] /api/missing - 404
```

## Note

- Questo è un esempio didattico per dimostrare l'uso di MicroTools
- Per un servizio di produzione, vedere `/project/install/services/mod_status`
- Le classi DB, Cursor, HttpRequest, HttpResponse hanno implementazioni stub nella libreria microtools
