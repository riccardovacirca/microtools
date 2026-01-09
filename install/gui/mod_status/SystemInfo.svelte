<script>
  import { onMount } from 'svelte';

  let systemInfo = null;
  let loading = true;
  let error = null;

  async function loadSystemInfo() {
    loading = true;
    error = null;
    try {
      const response = await fetch('/api/status/system');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      systemInfo = await response.json();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadSystemInfo();
  });
</script>

<div class="system-info">
  <div class="section-header">
    <h2>System Information</h2>
    <button class="refresh-btn" on:click={loadSystemInfo}>Refresh</button>
  </div>

  {#if loading}
    <div class="loading">Loading system information...</div>
  {:else if error}
    <div class="error">Error: {error}</div>
  {:else if systemInfo}
    <div class="info-grid">
      <div class="info-item">
        <span class="label">Hostname:</span>
        <span class="value">{systemInfo.hostname}</span>
      </div>
      <div class="info-item">
        <span class="label">Operating System:</span>
        <span class="value">{systemInfo.os_name}</span>
      </div>
      <div class="info-item">
        <span class="label">OS Version:</span>
        <span class="value">{systemInfo.os_version}</span>
      </div>
      <div class="info-item">
        <span class="label">Architecture:</span>
        <span class="value">{systemInfo.architecture}</span>
      </div>
      <div class="info-item">
        <span class="label">CPU Cores:</span>
        <span class="value">{systemInfo.cpu_cores}</span>
      </div>
      <div class="info-item">
        <span class="label">Total Memory:</span>
        <span class="value">{systemInfo.total_memory_mb} MB</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .system-info {
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
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .refresh-btn:hover {
    background: #1976D2;
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
