# MicroTools DSL Reference Documentation

Tutte le classi del DSL appartengono al namespace `microtools`.

Questo documento descrive le entità del DSL MicroTools con firme dei metodi, tipi di ritorno e tipi degli argomenti.

---

## Record

**Descrizione**: Singolo record chiave/valore.

**Costruttore**

* `Record()`

  * Ritorno: `Record`
  * Argomenti: nessuno

**Metodi**

* `set(key: string, value: std::any) -> void`
* `get(key: string) -> std::any`
* `has(key: string) -> bool`
* `merge(record: Record) -> void`
* `keys() -> vector<string>`
* `toString(format: Format = JSON) -> string`

---

## RecordSet

**Descrizione**: Collezione ordinata di `Record`.

**Costruttore**

* `RecordSet()`

  * Ritorno: `RecordSet`
  * Argomenti: nessuno

**Metodi**

* `add(record: Record) -> void`
* `get(index: size_t) -> Record*`
* `size() -> size_t`
* `empty() -> bool`
* `filter(predicate: function<bool(const Record&)>) -> RecordSet`
* `toString(format: Format = JSON) -> string`

---

## Cursor

**Descrizione**: Accesso sequenziale ai risultati da una sorgente dati.

**Costruttore**

* `Cursor()`

  * Ritorno: `Cursor`
  * Argomenti: nessuno

**Metodi**

* `next() -> unique_ptr<Record>`

---

## DB

**Descrizione**: Interfaccia unificata per l'accesso ai database.

**Costruttore**

* `DB(driver: string, connectionString: string)`

  * Ritorno: `DB`

**Metodi**

* `select(sql: string) -> unique_ptr<RecordSet>`
* `query(sql: string) -> int`
* `lastId() -> int`
* `cursor(sql: string) -> Cursor`

---

## File

**Descrizione**: Accesso uniforme ai file testuali.

**Costruttore**

* `File(path: string)`

  * Ritorno: `File`

**Metodi**

* `read() -> string`
* `write(data: string) -> void`
* `append(data: string) -> void`

---

## ExcelFile

**Descrizione**: Acquisizione del contenuto di file Excel.

**Costruttore**

* `ExcelFile(path: string)`

  * Ritorno: `ExcelFile`

**Metodi**

* (nessuno per il momento)

---

## JSON

**Descrizione**: Wrapper basato su nlohmann/json.

**Costruttore**

* `JSON()`

  * Ritorno: `JSON`

**Metodi**

* `add(key: string, value: std::any) -> void`
* `encode() -> string`
* `decode(jsonString: string) -> void`

---

## HttpRequest

**Descrizione**: Wrapper per la richiesta HTTP (httplib).

**Costruttore**

* `HttpRequest(nativeRequest: httplib::Request)`

  * Ritorno: `HttpRequest`

**Metodi**

* `getPath() -> vector<string>`
* `getUri() -> string`
* `getProtocol() -> string`
* `getMethod() -> string`
* `getHeaders() -> Map<string, string>`
* `getHeader(key: string) -> string`
* `getCookies() -> Map<string, string>`
* `getCookie(key: string) -> string`
* `getQuery() -> string`
* `getParams() -> Record`  (chiavi ripetute -> vector<string>)
* `getUploadedFiles() -> RecordSet`  (ogni Record contiene metadati file e path temporaneo)
* `getMultipartFields() -> Record`

---

## HttpResponse

**Descrizione**: Wrapper per la risposta HTTP (httplib). Il body è un `Record` con chiavi `err`, `log` e `out`.

**Costruttore**

* `HttpResponse()`

  * Ritorno: `HttpResponse`

**Metodi**

* `setHeader(key: string, value: string) -> void`
* `setContentType(value: string) -> void`
* `setStatus(status: int) -> void`
* `setBody(record: Record) -> void`
* `setCookie(key: string, value: string, path: string, exp: int) -> void`
* `download() -> void`

---

## Env

**Descrizione**: Accesso alle variabili ambiente.

**Costruttore**

* `Env()`

  * Ritorno: `Env`

**Metodi**

* `get(key: string) -> unique_ptr<string>`  (nullptr se non definita)

---

## Logger

**Descrizione**: Wrapper di spdlog per logging su file.

**Costruttore**

* `Logger(name: string, logFilePath: string)`

  * Ritorno: `Logger`
  * Argomenti:
    * `name`: Nome del logger
    * `logFilePath`: Path del file di log (crea directory se non esiste)

**Metodi**

* `info(message: string) -> void`
* `warn(message: string) -> void`
* `error(message: string) -> void`
* `debug(message: string) -> void`

**Formato log**: `[timestamp] [level] message`

**Livelli di log**: debug, info, warn, error

---

## Convenzioni generali del DSL

* Namespace: `microtools`
* Classi in PascalCase, metodi in camelCase
* Verbi coerenti (`set`, `add`, `get`, `select`, `query`)
* Indentazione a 2 spazi
* Uso obbligatorio di `std::unique_ptr` per risorse
* Tutti i valori delle mappe sono `std::any`
* Tutti i metodi che accettano o restituiscono mappe usano `Map<string, std::any>`
* Operazioni di lettura restituiscono oggetti del DSL o `nullptr`
* Operazioni di modifica restituiscono numeri di stato

### Formati di serializzazione

* `JSON` (default)
* `CSV` (; come separatore, stringhe tra doppi apici)

