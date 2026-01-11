<script>
  import { createEventDispatcher } from 'svelte';

  export let contatto;

  const dispatch = createEventDispatcher();

  const statoColors = {
    attivo: '#4caf50',
    inattivo: '#9e9e9e',
    prospect: '#2196f3',
    cliente: '#ff9800',
    lead: '#9c27b0',
    archiviato: '#607d8b'
  };

  const statoLabels = {
    attivo: 'Attivo',
    inattivo: 'Inattivo',
    prospect: 'Prospect',
    cliente: 'Cliente',
    lead: 'Lead',
    archiviato: 'Archiviato'
  };

  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT');
  }
</script>

<div class="contatto-card" class:deleted={contatto.deleted_at}>
  <div class="card-header">
    <div class="name-section">
      <h3>{contatto.nome} {contatto.cognome}</h3>
      {#if contatto.azienda}
        <p class="company">{contatto.azienda}</p>
      {/if}
      {#if contatto.ruolo}
        <p class="role">{contatto.ruolo}</p>
      {/if}
    </div>
    <span class="stato-badge" style="background-color: {statoColors[contatto.stato]}">
      {statoLabels[contatto.stato]}
    </span>
  </div>

  <div class="card-body">
    {#if contatto.email}
      <div class="info-row">
        <span class="icon">✉️</span>
        <a href="mailto:{contatto.email}">{contatto.email}</a>
      </div>
    {/if}

    {#if contatto.telefono}
      <div class="info-row">
        <span class="icon">📞</span>
        <a href="tel:{contatto.telefono}">{contatto.telefono}</a>
      </div>
    {/if}

    {#if contatto.cellulare}
      <div class="info-row">
        <span class="icon">📱</span>
        <a href="tel:{contatto.cellulare}">{contatto.cellulare}</a>
      </div>
    {/if}

    {#if contatto.citta || contatto.provincia}
      <div class="info-row">
        <span class="icon">📍</span>
        <span>{contatto.citta || ''} {contatto.provincia ? `(${contatto.provincia})` : ''}</span>
      </div>
    {/if}

    {#if contatto.liste && contatto.liste.length > 0}
      <div class="liste-section">
        <strong>Liste:</strong>
        <div class="liste-badges">
          {#each contatto.liste as lista}
            <span class="lista-badge">{lista.nome}</span>
          {/each}
        </div>
      </div>
    {/if}

    <div class="consensi-section">
      <label class:active={contatto.consenso_privacy}>
        {contatto.consenso_privacy ? '✓' : '✗'} Privacy
      </label>
      <label class:active={contatto.consenso_marketing}>
        {contatto.consenso_marketing ? '✓' : '✗'} Marketing
      </label>
    </div>

    {#if contatto.deleted_at}
      <div class="deleted-info">
        🗑️ Archiviato il {formatDate(contatto.deleted_at)}
      </div>
    {/if}
  </div>

  <div class="card-actions">
    {#if contatto.deleted_at}
      <button class="btn-restore" on:click={() => dispatch('restore')}>
        Ripristina
      </button>
      <button class="btn-delete-hard" on:click={() => dispatch('hardDelete')}>
        Elimina definitivamente
      </button>
    {:else}
      <button class="btn-edit" on:click={() => dispatch('edit')}>
        Modifica
      </button>
      <button class="btn-delete" on:click={() => dispatch('delete')}>
        Archivia
      </button>
    {/if}
  </div>
</div>

<style>
  .contatto-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .contatto-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  }

  .contatto-card.deleted {
    opacity: 0.7;
    background: #f5f5f5;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e0e0e0;
  }

  .name-section h3 {
    margin: 0 0 4px 0;
    color: #2c3e50;
    font-size: 18px;
  }

  .company {
    margin: 0;
    color: #666;
    font-weight: 500;
    font-size: 14px;
  }

  .role {
    margin: 0;
    color: #999;
    font-size: 13px;
  }

  .stato-badge {
    padding: 4px 12px;
    border-radius: 12px;
    color: white;
    font-size: 12px;
    font-weight: bold;
    white-space: nowrap;
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }

  .icon {
    width: 20px;
  }

  .info-row a {
    color: #2196f3;
    text-decoration: none;
  }

  .info-row a:hover {
    text-decoration: underline;
  }

  .liste-section {
    margin-top: 8px;
  }

  .liste-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
  }

  .lista-badge {
    padding: 2px 8px;
    background: #e3f2fd;
    border: 1px solid #2196f3;
    border-radius: 4px;
    font-size: 12px;
    color: #1976d2;
  }

  .consensi-section {
    display: flex;
    gap: 16px;
    margin-top: 8px;
    font-size: 13px;
  }

  .consensi-section label {
    color: #999;
  }

  .consensi-section label.active {
    color: #4caf50;
    font-weight: bold;
  }

  .deleted-info {
    margin-top: 8px;
    padding: 8px;
    background: #ffebee;
    border-radius: 4px;
    color: #c62828;
    font-size: 13px;
  }

  .card-actions {
    display: flex;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid #e0e0e0;
  }

  .card-actions button {
    flex: 1;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
  }

  .btn-edit {
    background: #2196f3;
    color: white;
  }

  .btn-edit:hover {
    background: #1976d2;
  }

  .btn-delete {
    background: #ff9800;
    color: white;
  }

  .btn-delete:hover {
    background: #f57c00;
  }

  .btn-restore {
    background: #4caf50;
    color: white;
  }

  .btn-restore:hover {
    background: #45a049;
  }

  .btn-delete-hard {
    background: #f44336;
    color: white;
  }

  .btn-delete-hard:hover {
    background: #d32f2f;
  }
</style>
