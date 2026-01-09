- [OK]
  Rendrere le classi della libreria microtools conformi al dsl c++
  aggiornato.

- [OK]
  Il file odbc.ini di configurazione di nanodbc deve avere un link simbolico
  alla cartella /workspace/conf. verificare dove la configurazione viene creata
  nello script di setup per aggiungere questo link.

- La prima operazione dell'installer potrebbe essere la copia della intera
  cartella. Nella cartella project invece della copia dei singoli file
  cartelle.

- [OK]
  Verificare che mod_status sia conforme al dsl
  /workspace/project/install/docs/dsl/python_models.json.

- [OK]
  Il setup dovrebbe installare gunicorn accanto a uvicorn e configurarli su
  porte diverse per poter eseguire dei test con gunicorn anche in fase di
  sviluppo.

- [OK]
  gli script di gestione dello stato di gunicorn dovrebbero essere integrati
  con lo script wa con dei subcommands dedicati
  es. wa gunicorn start|stop|restart|status.

- [OK] Verificare come vengono usate le variabili del file .env: PROJECT_NAME e
  NAME. dal momento che hanno lo stesso valore potremmo mantenere solo
  PROJECT_NAME

- Verificre se le variabili POLL_INTERVAL THREAD_COUNT possono essere rimosse

- [OK]
  modificare il comando wa update in 'wa git push' e aggiungere il comando
  'wa git pull' e inoltre aggiungere il comando 'wa git sync' per eseguire
  entrambe le operazioni nell'ordine più sensato

- integrare il framework grafico coreui nella cartella gui configurando nel file
  env la versione utilizzata e importandolo nella build della gui

- verificare che la libreria di logging di microtools utilizzi la cartella di
  log del progetto

- verificare come vengono configurati i services e la relazione con il file .env

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
  mediante /workspace/project/install/database/mod_status/sqlite3/data.sql.
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
  Attualmente esiste un comando wa gui build. Questo comando va sostituito con
  il comando wa vite wa vite build|start|stop|restart|status

- [OK]
  Lo script setup.sh a partire dalla riga 237 provvede ad installare i servizi
  gestiti da s6. Verificare se:
  > Uvicorn è denominato api
  > Gunicorn è completamente gestito mediante il contenuto di /workspace/project/install/s6/gunicorn
  > I servizi attualmente gestiti corrispondono a quelli definiti in /workspace/project/install/s6
  > Per tutti i servizi definiti in /workspace/project/install/s6 è assicurata
    la persistenza al riavvio del container
  > gli script /workspace/project/install/api/start.sh e /workspace/project/install/api/stop.sh
    non sono più necessari nella attuale gestione dei servizi

- [OK]
  Rimuovere gli script obsoleti:
  > /workspace/project/install/api/start.sh
  > /workspace/project/install/api/stop.sh
  Nella gestione s6 rinominare api in uvicorn in modo  
  che ci sia corrispondenza tra il nome e il servizio effettivamente gestito

- [OK]
  Il microservizio mod_status deve essere tra i servizi DEFAULT_ENABLED_SERVICES

- [OK]
  Nello script wa AG_STATUS si riferisce a uvicorn. modificare il nome AG_ in
  UVICORN_ e anche AG_ICON

- [OK]
  Il setup di claude con setup.sh deve copiare la cartella .claude in /workspace

- [OK]
  Verificare se nella gui mod_status dipende da /workspace/project/install/gui/mod_home
  Se non esiste nessuna dipendenza rimuovere mod_home e includere mod_status
  in /workspace/project/install/gui/Layout.svelte al suo posto

- rendere minimalista l'output del comando wa

- rinominare il progetto in microtools

- rinominare il comando wa in mt

- le cartelle project e install potrebbero essere prefissate con un . come le
  altre tabelle di servizio. la cartella project

- il comando wa git push potrebbe avere una opzione -m per il messaggio di commit
  se non specificato viene usato il messaggio di default

- Verificare che il modulo mod_status della gui sia collegato correttamente
  agli endpoint.