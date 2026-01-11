<script>
  import { onMount } from 'svelte';
  import ContattoCardComponent from './ContattoCardComponent.svelte';
  import ContattoFormComponent from './ContattoFormComponent.svelte';

  let contatti = [];
  let loading = true;
  let error = null;
  let currentPage = 1;
  let totalPages = 1;
  let totalContatti = 0;
  let searchQuery = '';
  let showForm = false;
  let editingContatto = null;
  let includeDeleted = false;

  const pageSize = 20;

  async function loadContatti() {
    loading = true;
    error = null;

    try {
      let url = `/api/contatti?page=${currentPage}&page_size=${pageSize}&include_deleted=${includeDeleted}`;

      if (searchQuery.trim()) {
        url = `/api/contatti/search?q=${encodeURIComponent(searchQuery)}&page=${currentPage}&page_size=${pageSize}`;
      }

      const response = await fetch(url, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Errore nel caricamento dei contatti');
      }

      const data = await response.json();
      contatti = data.contatti || [];
      totalContatti = data.total || 0;
      totalPages = Math.ceil(totalContatti / pageSize);
    } catch (err) {
      error = err.message;
      console.error('Error loading contatti:', err);
    } finally {
      loading = false;
    }
  }

  function handleSearch() {
    currentPage = 1;
    loadContatti();
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      loadContatti();
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      loadContatti();
    }
  }

  function handleNew() {
    editingContatto = null;
    showForm = true;
  }

  function handleEdit(contatto) {
    editingContatto = contatto;
    showForm = true;
  }

  async function handleDelete(contattoId, isHard = false) {
    const confirmMsg = isHard
      ? 'Sei sicuro di voler eliminare PERMANENTEMENTE questo contatto?'
      : 'Sei sicuro di voler archiviare questo contatto?';

    if (!confirm(confirmMsg)) return;

    try {
      const endpoint = isHard ? `/api/contatti/${contattoId}/hard` : `/api/contatti/${contattoId}/soft`;
      const response = await fetch(endpoint, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        await loadContatti();
      } else {
        alert('Errore durante l\'eliminazione del contatto');
      }
    } catch (err) {
      console.error('Error deleting contatto:', err);
      alert('Errore durante l\'eliminazione del contatto');
    }
  }

  async function handleRestore(contattoId) {
    try {
      const response = await fetch(`/api/contatti/${contattoId}/restore`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        await loadContatti();
      } else {
        alert('Errore durante il ripristino del contatto');
      }
    } catch (err) {
      console.error('Error restoring contatto:', err);
      alert('Errore durante il ripristino del contatto');
    }
  }

  function handleFormClose() {
    showForm = false;
    editingContatto = null;
    loadContatti();
  }

  onMount(() => {
    loadContatti();
  });
</script>

<div class="contatti-container">
  <div class="header">
    <h1>Gestione Contatti</h1>
    <button class="btn-primary" on:click={handleNew}>+ Nuovo Contatto</button>
  </div>

  <div class="toolbar">
    <div class="search-bar">
      <input
        type="text"
        placeholder="Cerca contatti..."
        bind:value={searchQuery}
        on:keyup={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button class="btn-search" on:click={handleSearch}>Cerca</button>
      {#if searchQuery}
        <button class="btn-clear" on:click={() => { searchQuery = ''; handleSearch(); }}>Cancella</button>
      {/if}
    </div>

    <label class="checkbox-label">
      <input type="checkbox" bind:checked={includeDeleted} on:change={loadContatti} />
      Mostra archiviati
    </label>
  </div>

  {#if loading}
    <div class="loading">Caricamento...</div>
  {:else if error}
    <div class="error">Errore: {error}</div>
  {:else if contatti.length === 0}
    <div class="empty">Nessun contatto trovato</div>
  {:else}
    <div class="contatti-grid">
      {#each contatti as contatto (contatto.id)}
        <ContattoCardComponent
          {contatto}
          on:edit={() => handleEdit(contatto)}
          on:delete={() => handleDelete(contatto.id, false)}
          on:hardDelete={() => handleDelete(contatto.id, true)}
          on:restore={() => handleRestore(contatto.id)}
        />
      {/each}
    </div>

    <div class="pagination">
      <button class="btn-page" disabled={currentPage === 1} on:click={prevPage}>
        ← Precedente
      </button>
      <span class="page-info">
        Pagina {currentPage} di {totalPages} ({totalContatti} contatti)
      </span>
      <button class="btn-page" disabled={currentPage === totalPages} on:click={nextPage}>
        Successiva →
      </button>
    </div>
  {/if}
</div>

{#if showForm}
  <ContattoFormComponent contatto={editingContatto} on:close={handleFormClose} />
{/if}

<style>
  .contatti-container {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  h1 {
    margin: 0;
    color: #2c3e50;
  }

  .toolbar {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    align-items: center;
  }

  .search-bar {
    display: flex;
    gap: 10px;
    flex: 1;
  }

  input[type="text"] {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .btn-primary {
    background: #2196f3;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }

  .btn-primary:hover {
    background: #1976d2;
  }

  .btn-search, .btn-clear {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn-search {
    background: #4caf50;
    color: white;
  }

  .btn-search:hover {
    background: #45a049;
  }

  .btn-clear {
    background: #ff9800;
    color: white;
  }

  .btn-clear:hover {
    background: #f57c00;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }

  .contatti-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }

  .loading, .error, .empty {
    text-align: center;
    padding: 40px;
    color: #666;
    font-size: 16px;
  }

  .error {
    color: #f44336;
  }

  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 30px;
  }

  .btn-page {
    padding: 10px 20px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn-page:hover:not(:disabled) {
    background: #f5f5f5;
  }

  .btn-page:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-info {
    color: #666;
  }
</style>
