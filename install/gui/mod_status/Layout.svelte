<script>
  import SystemInfo from './SystemInfo.svelte';
  import ProjectInfo from './ProjectInfo.svelte';

  let activeTab = 'system';

  const tabs = [
    { id: 'system', label: 'System Information' },
    { id: 'project', label: 'Project Information' }
  ];

  function selectTab(tabId) {
    activeTab = tabId;
  }
</script>

<div class="status-container">
  <header class="status-header">
    <h1>System Status Dashboard</h1>
    <p>System and project information</p>
  </header>

  <nav class="tabs">
    {#each tabs as tab}
      <button
        class="tab {activeTab === tab.id ? 'active' : ''}"
        on:click={() => selectTab(tab.id)}
      >
        {tab.label}
      </button>
    {/each}
  </nav>

  <main class="tab-content">
    {#if activeTab === 'system'}
      <SystemInfo />
    {:else if activeTab === 'project'}
      <ProjectInfo />
    {/if}
  </main>
</div>

<style>
  .status-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .status-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .status-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
    color: #333;
  }

  .status-header p {
    color: #666;
    font-size: 1rem;
  }

  .tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 0;
  }

  .tab {
    padding: 12px 24px;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 1rem;
    color: #666;
    border-bottom: 3px solid transparent;
    transition: all 0.3s;
  }

  .tab:hover {
    color: #333;
    background: #f5f5f5;
  }

  .tab.active {
    color: #2196F3;
    border-bottom-color: #2196F3;
  }

  .tab-content {
    padding: 20px 0;
  }
</style>
