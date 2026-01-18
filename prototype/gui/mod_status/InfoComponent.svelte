<script>
  import { onMount } from "svelte";

  let Info = null;
  let loading = true;
  let error = null;

  async function loadInfo() {
    loading = true;
    error = null;
    try {
      const response = await fetch("/api/status/info");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      Info = await response.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadInfo();
  });
</script>

<div class="project-info">
  <div class="section-header">
    <h2>Project Information</h2>
    <button class="refresh-btn" on:click={loadInfo}>Refresh</button>
  </div>

  {#if loading}
    <div class="loading">Loading project information...</div>
  {:else if error}
    <div class="error">Error: {error}</div>
  {:else if Info}
    <div class="info-grid">
      <div class="info-item">
        <span class="label">ID:</span>
        <span class="value">{Info.id}</span>
      </div>
      <div class="info-item">
        <span class="label">Version:</span>
        <span class="value">{Info.version}</span>
      </div>
      <div class="info-item">
        <span class="label">Created At:</span>
        <span class="value">{Info.created_at}</span>
      </div>
      <div class="info-item">
        <span class="label">Updated At:</span>
        <span class="value">{Info.updated_at}</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .project-info {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
  }

  .refresh-btn {
    padding: 8px 16px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .refresh-btn:hover {
    background: #1976d2;
  }

  .loading,
  .error {
    padding: 20px;
    text-align: center;
    color: #666;
  }

  .error {
    color: #f44336;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    background: #f5f5f5;
    border-radius: 4px;
  }

  .info-item .label {
    font-weight: 600;
    color: #555;
  }

  .info-item .value {
    color: #333;
  }
</style>
