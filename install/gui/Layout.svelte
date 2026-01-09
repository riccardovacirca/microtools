<script>
  import { onMount } from 'svelte'
  import { auth, checkAuth } from './store.js'
  import StatusLayout from './mod_status/Layout.svelte'

  let loading = true

  onMount(async () => {
    await checkAuth()
    loading = false
  })
</script>

{#if loading}
  <div class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Caricamento...</span>
    </div>
  </div>
{:else if $auth.token}
  <!-- Blocco autenticato -->
  <StatusLayout />
{:else}
  <!-- Blocco non autenticato -->
  <div class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="text-center">
      <h3>Accesso richiesto</h3>
      <p class="text-muted">L'autenticazione è richiesta per accedere a questa applicazione.</p>
    </div>
  </div>
{/if}

<style></style>
