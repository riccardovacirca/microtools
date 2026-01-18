- [OK]
  Rendrere le classi della libreria microtools conformi al dsl c++
  aggiornato.

- [OK]
  Il file odbc.ini di configurazione di nanodbc deve avere un link simbolico
  alla cartella /workspace/conf. verificare dove la configurazione viene creata
  nello script di setup per aggiungere questo link.

- [OK]
  Verificare che mod_status sia conforme al dsl
  /workspace/.prototype/install/docs/dsl/python_models.json.

- [OK]
  Il setup dovrebbe installare gunicorn accanto a uvicorn e configurarli su
  porte diverse per poter eseguire dei test con gunicorn anche in fase di
  sviluppo.

- [OK]
  gli script di gestione dello stato di gunicorn dovrebbero essere integrati
  con lo script mt con dei subcommands dedicati
  es. mt gunicorn start|stop|restart|status.

- [OK] Verificare come vengono usate le variabili del file .env: PROJECT_NAME e
  NAME. dal momento che hanno lo stesso valore potremmo mantenere solo
  PROJECT_NAME

- Verificre se le variabili POLL_INTERVAL THREAD_COUNT possono essere rimosse

- [OK]
  modificare il comando mt update in 'wa git push' e aggiungere il comando
  'wa git pull' e inoltre aggiungere il comando 'wa git sync' per eseguire
  entrambe le operazioni nell'ordine più sensato

- [OK]
  Installare la libreria redis-py (pip install redis) durante la procedura
  di setup dello script setup.sh

- [OK]
  Installare la libreria hiredis c++ duarante la procedura di setup dello script
  setup.sh aggiungendo la dipendenza apt libhiredis-dev.

- [OK]
  Aggiungere a microtools una libreria Redis.h Redis.cpp wrapper di hiredis.
  secondo la filosofia minimalista della libreria microtools da hiredis dobbiamo
  importare solo le funzioni essnziali per:
  > listare le chiavi esistenti
  > leggere/scrivere/aggiornare il valore di una chiave 
  > rimuovere una chiave

- [OK]
  aggiungere ad /workspace/api/common una libreria wrapper di redis-py per:
  > listare le chiavi esistenti
  > leggere/scrivere/aggiornare il valore di una chiave 
  > rimuovere una chiave 

- [OK]
  mod_status deve esporre il solo endpoint info corrispondente alla rotta
  /api/status/info. la logica deve essere la seguente. quando il modulo python
  riceve la richiesta estrae da redis la chiave app_status e restituisce il
  valore al client. se la chiave non esiste invoca il microservizio c++ mediante
  l'adapter sulla porta 9001/api/status/info e restituisce lo stato della app
  al client

- [OK]
  modificare il microservizio c++ mod_status in modo che verifichi l'esistenza
  di una chiave app_status su redis corrispondente al recod sql inserito
  mediante /workspace/.prototype/install/database/mod_status/sqlite3/data.sql.
  se la chiave esiste legge il valore e restituisce il dato opportunamente
  serializzato in json al client altrimenti apre una connessione con il db,
  legge il record dal database, genera la chiave app_status con il record letto
  opportunamente serializzato per redis e restituisce al client lo stesso dato.
  Se su redis il dato non è salvato come json, prima di restituire il dato al
  client il dato va serializzato in json secondo il formato della ResponseHttp.

- [OK]
  verificare che i servizi gestiti da s6 possano essere
  arrestati/avviati/riavviati manualmente nel modo seguente:
  > riavvia il servizio (stop + start)
    s6-svc -r /path/to/s6/services/<nome_servizio>
  > ferma
    s6-svc -d /path/to/s6/services/<nome_servizio>
  > avvia
    s6-svc -u /path/to/s6/services/<nome_servizio>

- [OK]
  Attualmente esiste un comando mt gui build. Questo comando va sostituito con
  il comando mt vite mt vite build|start|stop|restart|status

- [OK]
  Lo script setup.sh a partire dalla riga 237 provvede ad installare i servizi
  gestiti da s6. Verificare se:
  > Uvicorn è denominato api
  > Gunicorn è completamente gestito mediante il contenuto di /workspace/.prototype/install/s6/gunicorn
  > I servizi attualmente gestiti corrispondono a quelli definiti in /workspace/.prototype/install/s6
  > Per tutti i servizi definiti in /workspace/.prototype/install/s6 è assicurata
    la persistenza al riavvio del container
  > gli script /workspace/.prototype/install/api/start.sh e /workspace/.prototype/install/api/stop.sh
    non sono più necessari nella attuale gestione dei servizi

- [OK]
  Rimuovere gli script obsoleti:
  > /workspace/.prototype/install/api/start.sh
  > /workspace/.prototype/install/api/stop.sh
  Nella gestione s6 rinominare api in uvicorn in modo  
  che ci sia corrispondenza tra il nome e il servizio effettivamente gestito

- [OK]
  Il microservizio mod_status deve essere tra i servizi DEFAULT_ENABLED_SERVICES

- [OK]
  Nello script mt AG_STATUS si riferisce a uvicorn. modificare il nome AG_ in
  UVICORN_ e anche AG_ICON

- [OK]
  Il setup di claude con setup.sh deve copiare la cartella .claude in /workspace

- [OK]
  Verificare se nella gui mod_status dipende da /workspace/.prototype/install/gui/mod_home
  Se non esiste nessuna dipendenza rimuovere mod_home e includere mod_status
  in /workspace/.prototype/install/gui/Layout.svelte al suo posto

- [OK]
  rinominare il progetto in microtools

- [OK]
  rinominare il comando wa in mt

- [OK]
  Verificare che il modulo /workspace/gui/src/mod_status della gui sia collegato
  correttamente all'endpoint /api/status/info ed esponga graficamente il valore
  restituito da esso.

- integrare il framework grafico coreui nella cartella gui configurando nel file
  env la versione utilizzata e importandolo nella build della gui

- verificare che la libreria di logging di microtools utilizzi la cartella di
  log del progetto

- verificare come vengono configurati i services e la relazione con il file .env

- aggiungere al file setup.sh l'installazione dei pacchetti apt nano e tree nel
  container di sviluppo 

- La gestione delle librerie avviene secondo il seguente schema che deve essere
  implementato durante la procedura di setup:
  
  workspace/
  '--> .prototype/
  |    '--> install/
  |         '--> lib/
  |              '--> cpp/
  |              '--> python/
  '--> api/
  |    '--> lib/
  |         '--> microtools/ (ln -s to /workspace/.prototype/install/lib/python)
  '--> service
  |    '--> lib/
  |         '--> microtools/ (ln -s to /workspace/.prototype/install/lib/cpp)

  Il path /workspace/service/lib/microtools/ potrebbe essere aggiunto al path di
  sistema per permettere di trovare il file microtools.a durante la procedura di
  compilazione

- La modalità ammessa per utilizzare i microservizi è attraverso i
  componenti della GUI in JavaScript nel modo seguente:
  > La GUI richiede una azione collegata a un microservizio mediante un
    adapter eseguendo una chiamata verso un endpoint. Es.:
    curl -X GET http://localhost:2310/api/status/info
  > Internamente l'adapter invoca il microservizio C++ e ottiene il job_id
    curl -X POST http://127.0.0.1:9001/api/status/info -> {"job_id":"abc123"}
  > L'adapter restituisce il job_id alla GUI risalendo lo stack API.
  > La GUI apre un canale ws verso il microservizio passandogli il job_id
    ws://127.0.0.1:9001/ws/.../{job_id} e renderizza lo stato dell'operazione
    in base alla risposta ottenuta:
    {"status": "work", result: null}
    {"status": "done", result: null|data|Redis key}
    {"status": "fail", result: null}
  > Al termine il microservizio può:
    > Salvare il risultato su redis e restituire la chiave alla GUI
    > Restituire direttamente il risultato alla GUI

- Implementare la logica GUI/FastAPI via SSE + FastAPI/Microservice via WS

- L'installazione corrente di fastAPI nella cartella /workspace/api avviene durante la procedura di setup a carico del file setup.sh . questa installazione prevede una struttura modulare del progetto fastAPI . i moduli come ad esempio mod_status devono usare una libreria comune. attualmente stiamo migrando questa libreria. in precedenza questa libreria era implementata nella cartella /workspace/api/common.backup ma adesso la decisione è quella di utilizzare la libreria presente in /workspace/.prototype/install/lib/utils/python così come avviene per la libreria cpp anche questa libreria dovrebbe essere copiata dalla sua posizione attuale che è la posizione di origine nella posizione /workspace/api/utils e utilizzata da questa posizione. questa copia deve avvenire durante la procedura di setup eseguita dal file setup.sh. tutti i moduli dovrebbero usare gli script di questa libreria per le operazioni comuni che per il momento sono parzialmente implementate. Attualmente infatti i moduli python in apii sono solo parzialmente funzionanti perchè la  libreria è ancora incompleta. per il momento occupiamoci del setup che copia la libreria poi implementeremo e correggeremo i moduli

- rimuovere il link simbolico a install e modificare tutti i percorsi in
  setup.sh, install.sh, e bin/mt

- rinominare .prototype in .microtools e install in prototype
  in modo da avere una struttura .microtools/prototype che rappresenta il
  prototipo della applicazione

- rinominare mt in cmd

- rifattorizzare la procedura di release. spostare il file release
  allo stesso livello di setup e spostare la cartella release dentro
  .microtools/prototype/release aggiornando i percorsi in modo da esprimere il concetto di un prototipo della release

- rinominare /Users/riccardo/hello/.prototype/PROJECT.md in README.md
  aggiungere un file LICENSE

- eseguire una revisione manuale di install.sh setup.sh release.sh e cmd

- rendere minimalista l'output del comando cmd

- il comando mt git push potrebbe avere una opzione -m per il messaggio di commit
  se non specificato viene usato il messaggio di default



--------------------------------------------------------------------------------

docker pull ollama/ollama:latest
docker run -d --network hello-net -p 2377:11434 -v ollama:/root/.ollama --name ollama ollama/ollama:latest
docker exec -it hello bash 
curl -fsSL https://opencode.ai/install | bash
cd /root
cd .config/opencode
nano opencode.json

{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Llama 3.2 Local",
      "options": {
        "baseURL": "ollama:11434/v1"
      },
      "models": {
        "llama3.2:1b": {
          "name": "Llama 3.2 1B"
        }
      }
    }
  }
}
