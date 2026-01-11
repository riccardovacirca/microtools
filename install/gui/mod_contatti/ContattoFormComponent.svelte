<script>
  import { onMount, createEventDispatcher } from 'svelte';

  export let contatto = null;

  const dispatch = createEventDispatcher();

  let formData = {
    nome: '',
    cognome: '',
    email: '',
    telefono: '',
    cellulare: '',
    azienda: '',
    ruolo: '',
    indirizzo: '',
    citta: '',
    provincia: '',
    cap: '',
    paese: 'Italia',
    stato: 'prospect',
    consenso_privacy: false,
    consenso_marketing: false,
    note: '',
    liste_ids: []
  };

  let liste = [];
  let loading = false;
  let error = null;

  const statiOptions = [
    { value: 'attivo', label: 'Attivo' },
    { value: 'inattivo', label: 'Inattivo' },
    { value: 'prospect', label: 'Prospect' },
    { value: 'cliente', label: 'Cliente' },
    { value: 'lead', label: 'Lead' },
    { value: 'archiviato', label: 'Archiviato' }
  ];

  async function loadListe() {
    try {
      const response = await fetch('/api/contatti/liste', {
        credentials: 'include'
      });

      if (response.ok) {
        liste = await response.json();
      }
    } catch (err) {
      console.error('Error loading liste:', err);
    }
  }

  async function handleSubmit() {
    loading = true;
    error = null;

    try {
      const url = contatto ? `/api/contatti/${contatto.id}` : '/api/contatti';
      const method = contatto ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Errore durante il salvataggio');
      }

      dispatch('close');
    } catch (err) {
      error = err.message;
      console.error('Error saving contatto:', err);
    } finally {
      loading = false;
    }
  }

  function handleCancel() {
    dispatch('close');
  }

  function toggleLista(listaId) {
    const index = formData.liste_ids.indexOf(listaId);
    if (index > -1) {
      formData.liste_ids = formData.liste_ids.filter(id => id !== listaId);
    } else {
      formData.liste_ids = [...formData.liste_ids, listaId];
    }
  }

  onMount(async () => {
    await loadListe();

    if (contatto) {
      formData = {
        nome: contatto.nome || '',
        cognome: contatto.cognome || '',
        email: contatto.email || '',
        telefono: contatto.telefono || '',
        cellulare: contatto.cellulare || '',
        azienda: contatto.azienda || '',
        ruolo: contatto.ruolo || '',
        indirizzo: contatto.indirizzo || '',
        citta: contatto.citta || '',
        provincia: contatto.provincia || '',
        cap: contatto.cap || '',
        paese: contatto.paese || 'Italia',
        stato: contatto.stato || 'prospect',
        consenso_privacy: contatto.consenso_privacy || false,
        consenso_marketing: contatto.consenso_marketing || false,
        note: contatto.note || '',
        liste_ids: contatto.liste ? contatto.liste.map(l => l.id) : []
      };
    }
  });
</script>

<div class="modal-backdrop" on:click={handleCancel}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>{contatto ? 'Modifica Contatto' : 'Nuovo Contatto'}</h2>
      <button class="btn-close" on:click={handleCancel}>×</button>
    </div>

    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-grid">
        <div class="form-section">
          <h3>Dati Anagrafici</h3>

          <div class="form-row">
            <div class="form-group">
              <label for="nome">Nome *</label>
              <input id="nome" type="text" bind:value={formData.nome} required />
            </div>

            <div class="form-group">
              <label for="cognome">Cognome *</label>
              <input id="cognome" type="text" bind:value={formData.cognome} required />
            </div>
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input id="email" type="email" bind:value={formData.email} />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="telefono">Telefono</label>
              <input id="telefono" type="tel" bind:value={formData.telefono} />
            </div>

            <div class="form-group">
              <label for="cellulare">Cellulare</label>
              <input id="cellulare" type="tel" bind:value={formData.cellulare} />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3>Informazioni Professionali</h3>

          <div class="form-group">
            <label for="azienda">Azienda</label>
            <input id="azienda" type="text" bind:value={formData.azienda} />
          </div>

          <div class="form-group">
            <label for="ruolo">Ruolo</label>
            <input id="ruolo" type="text" bind:value={formData.ruolo} />
          </div>

          <div class="form-group">
            <label for="stato">Stato *</label>
            <select id="stato" bind:value={formData.stato} required>
              {#each statiOptions as option}
                <option value={option.value}>{option.label}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-section">
          <h3>Indirizzo</h3>

          <div class="form-group">
            <label for="indirizzo">Indirizzo</label>
            <input id="indirizzo" type="text" bind:value={formData.indirizzo} />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="citta">Città</label>
              <input id="citta" type="text" bind:value={formData.citta} />
            </div>

            <div class="form-group">
              <label for="provincia">Prov.</label>
              <input id="provincia" type="text" bind:value={formData.provincia} maxlength="2" />
            </div>

            <div class="form-group">
              <label for="cap">CAP</label>
              <input id="cap" type="text" bind:value={formData.cap} maxlength="10" />
            </div>
          </div>

          <div class="form-group">
            <label for="paese">Paese</label>
            <input id="paese" type="text" bind:value={formData.paese} />
          </div>
        </div>

        <div class="form-section">
          <h3>Consensi e Liste</h3>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" bind:checked={formData.consenso_privacy} />
              Consenso Privacy
            </label>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" bind:checked={formData.consenso_marketing} />
              Consenso Marketing
            </label>
          </div>

          {#if liste.length > 0}
            <div class="form-group">
              <label>Liste di appartenenza</label>
              <div class="liste-checkboxes">
                {#each liste as lista}
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData.liste_ids.includes(lista.id)}
                      on:change={() => toggleLista(lista.id)}
                    />
                    {lista.nome}
                  </label>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <div class="form-section full-width">
          <h3>Note</h3>
          <div class="form-group">
            <textarea
              id="note"
              bind:value={formData.note}
              rows="4"
              placeholder="Note aggiuntive..."
            ></textarea>
          </div>
        </div>
      </div>

      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      <div class="form-actions">
        <button type="button" class="btn-secondary" on:click={handleCancel} disabled={loading}>
          Annulla
        </button>
        <button type="submit" class="btn-primary" disabled={loading}>
          {loading ? 'Salvataggio...' : 'Salva'}
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    overflow-y: auto;
    padding: 20px;
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    width: 100%;
    max-width: 900px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
  }

  .modal-header h2 {
    margin: 0;
    color: #2c3e50;
  }

  .btn-close {
    background: none;
    border: none;
    font-size: 32px;
    color: #999;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    line-height: 1;
  }

  .btn-close:hover {
    color: #333;
  }

  form {
    padding: 20px;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }

  .form-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .form-section.full-width {
    grid-column: 1 / -1;
  }

  .form-section h3 {
    margin: 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #2196f3;
    color: #2c3e50;
    font-size: 16px;
  }

  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  label {
    font-weight: 500;
    color: #555;
    font-size: 14px;
  }

  input[type="text"],
  input[type="email"],
  input[type="tel"],
  select,
  textarea {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
  }

  input:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: #2196f3;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-weight: normal;
  }

  .checkbox-label input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  .liste-checkboxes {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px;
    background: #f5f5f5;
    border-radius: 4px;
  }

  .error-message {
    background: #ffebee;
    color: #c62828;
    padding: 12px;
    border-radius: 4px;
    margin-top: 16px;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
  }

  .btn-primary,
  .btn-secondary {
    padding: 10px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
  }

  .btn-primary {
    background: #2196f3;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #1976d2;
  }

  .btn-secondary {
    background: #e0e0e0;
    color: #333;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #d0d0d0;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    .form-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
