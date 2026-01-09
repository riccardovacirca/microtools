# Workflow mod_status

## Descrizione
Modulo per il monitoraggio dello stato e delle informazioni di runtime del sistema attraverso integrazione con servizio C++ mod_status.

## Dominio
Questo modulo gestisce le informazioni di stato del sistema, fornendo visibilità sullo stato di salute e le metriche runtime dei microservizi C++.

## Stati
- **Service Available**: Il servizio C++ mod_status risponde correttamente e fornisce informazioni
- **Service Unavailable**: Il servizio C++ mod_status non è raggiungibile o risponde con errore

## Transizioni
1. **GET /info** 
   - Input: Richiesta HTTP GET
   - Azione: Recupera informazioni runtime dal servizio C++ mod_status
   - Output: JSON con informazioni di stato, versione, ambiente
   - Stati: Service Available → Service Available (successo)
   - Stati: Service Available → Service Unavailable (timeout/errore connessione)

## Entità
- **RuntimeInfo**: Informazioni di runtime del servizio (versione, uptime, configurazione)
- **HealthStatus**: Stato di salute del servizio (disponibile/non disponibile)

## Regole di Dominio
- Le informazioni di runtime sono recuperate in tempo reale dal servizio C++
- In caso di indisponibilità del servizio C++, viene ritornato errore HTTP 503
- Non vengono effettuate operazioni di caching per garantire dati aggiornati
