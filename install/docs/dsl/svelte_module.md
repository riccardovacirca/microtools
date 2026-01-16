MODULE_STYLE hierarchical_layout_architecture

# ARCHITECTURE

PRINCIPLE: Separazione tra layout (routing/visibilità) e componenti (logica applicativa)

HIERARCHY:
  - Levels: module -> entity -> subentity
  - Max depth: 3 livelli
  - Rationale: Profondità limitata per garantire gestibilità

IMPORT STYLE:
  - Type: static imports only
  - Required: import Component from './path/Component.svelte'
  - Forbidden: dynamic import ({#await import(...)})
  - Rationale: Import statici garantiscono stabilità e prevedibilità

# DIRECTORY STRUCTURE

```
mod_<module_name>/
├── Layout.svelte                    # Entry point (importato da src/Layout.svelte)
├── <EntityName>Layout.svelte        # Entity layout (1 per entità)
├── store.js                         # Store unico centralizzato
├── <entity_name>/                   # Cartella entità (snake_case)
│   ├── <ComponentName>Component.svelte
│   └── ... (se semplice)
│   oppure (se complesso):
│   ├── <SubentityName>Layout.svelte
│   └── <subentity_name>/            # Cartella sub-entità
│       └── <ComponentName>Component.svelte
```

# NAMING CONVENTIONS

LAYOUTS:
  - Pattern: <Name>Layout.svelte
  - Case: PascalCase
  - Suffix: Layout
  - Examples:
    - Layout.svelte (entry point modulo)
    - ContattiLayout.svelte (entity layout)
    - DettaglioLayout.svelte (subentity layout)

COMPONENTS:
  - Pattern: <Name>Component.svelte
  - Case: PascalCase
  - Suffix: Component
  - Examples: ListaComponent.svelte, FormComponent.svelte, TabellaComponent.svelte

FOLDERS:
  - Case: snake_case
  - Examples: contatti, liste, campagne, dettaglio_contatto

STORE:
  - Name: store.js
  - Location: module root only (mai nelle sottocartelle)

# LAYOUT RULES

RESPONSIBILITY:
  Allowed:
    - Import statici di componenti e sub-layout
    - Routing via {#if}/{:else if} basato su stato
    - Passaggio props ai componenti figli
    - Navigazione e visibilità

  Forbidden:
    - Logica applicativa
    - Chiamate API dirette
    - Gestione stato complesso
    - Manipolazione dati
    - Business logic

STATE MANAGEMENT:
  - Navigation state: gestito nel layout (currentView, activeTab)
  - Application state: gestito nello store centralizzato
  - Local state: gestito nei componenti

PROP PASSING:
  - Pattern: export let propName
  - Direction: top-down (layout -> component)
  - Example: <ContattiLayout {currentView} />

# COMPONENT RULES

RESPONSIBILITY:
  Required:
    - Logica applicativa completa
    - Chiamate API
    - Gestione stato locale
    - Interazioni utente
    - Rendering UI
    - Event handling

  Forbidden:
    - Decisione sulla propria visibilità (compete al layout)
    - Import di altri layout
    - Gestione navigazione globale

VISIBILITY RULE:
  - Principle: Il componente si occupa solo del rendering
  - Decision: Sempre delegata al layout parent
  - Pattern: Layout decide {#if show}<Component />{/if}
  - Component: renderizza sempre, non decide se mostrarsi

STORE ACCESS:
  - Import: import { storeName } from '../store.js'
  - Usage: lettura e scrittura stato condiviso

# STORE RULES

LOCATION: mod_<module_name>/store.js
SCOPE: Unico per modulo
CENTRALIZATION: Obbligatoria (no store multipli)

CONTENT:
  - Stato condiviso del modulo
  - Derived state
  - Actions/mutations

IMPORT PATTERN:
  - From entity: import { state } from '../store.js'
  - From subentity: import { state } from '../../store.js'

# IMPORT PATTERNS

MODULE LAYOUT imports:
  - Entity layouts
  - Example: import ContattiLayout from './ContattiLayout.svelte'

ENTITY LAYOUT imports:
  - Components from entity folder OR subentity layouts
  - Simple: import ListaComponent from './contatti/ListaComponent.svelte'
  - Complex: import DettaglioLayout from './contatti/DettaglioLayout.svelte'

SUBENTITY LAYOUT imports:
  - Components from subentity folder only
  - Example: import FormComponent from './dettaglio/FormComponent.svelte'

FORBIDDEN:
  - Dynamic imports: {#await import('./Component.svelte')}
  - Cross-entity component imports
  - Store imports in layouts (solo stato navigazione locale)

# DATA FLOW

NAVIGATION:
  Flow: Layout.svelte -> EntityLayout -> Component
  State: currentView passed as prop or managed in layout

APPLICATION DATA:
  Flow: store.js <-> Components
  Pattern: Components read/write to centralized store

API CALLS:
  Location: Components only
  Forbidden in: Layouts

# ANTI-PATTERNS

FORBIDDEN:
  ✗ Dynamic imports
    Example: {#await import('./Component.svelte')}
    Reason: Meno stabile, comportamento imprevedibile

  ✗ Logic in layouts
    Example: API calls, data manipulation in Layout.svelte
    Reason: Layouts devono essere puri routing/visibility

  ✗ Self visibility decision
    Example: Component che decide {#if shouldShow} internamente
    Reason: Visibilità compete al layout parent

  ✗ Multiple stores
    Example: store.js in ogni sottocartella
    Reason: Store deve essere unico e centralizzato

  ✗ Deep nesting
    Example: subentity/sub-subentity/sub-sub-subentity
    Reason: Max 3 livelli: module -> entity -> subentity

  ✗ Cross-entity imports
    Example: contatti/ importing from liste/
    Reason: Entità devono essere autonome

  ✗ Wrong naming
    Examples: contatti.svelte, contattiComponent.svelte, Contatti/
    Reason: Naming conventions garantiscono consistenza

# EXAMPLES

## Module Layout (Entry Point)

File: mod_risorse/Layout.svelte
```svelte
<script>
  import ContattiLayout from './ContattiLayout.svelte';
  import ListeLayout from './ListeLayout.svelte';
  import CampagneLayout from './CampagneLayout.svelte';

  let currentView = $state('contatti');
</script>

<nav>
  <button onclick={() => currentView = 'contatti'}>Contatti</button>
  <button onclick={() => currentView = 'liste'}>Liste</button>
  <button onclick={() => currentView = 'campagne'}>Campagne</button>
</nav>

<main>
  {#if currentView === 'contatti'}
    <ContattiLayout />
  {:else if currentView === 'liste'}
    <ListeLayout />
  {:else if currentView === 'campagne'}
    <CampagneLayout />
  {/if}
</main>
```

## Entity Layout (Simple)

File: mod_risorse/ContattiLayout.svelte
```svelte
<script>
  import ListaComponent from './contatti/ListaComponent.svelte';
  import FormComponent from './contatti/FormComponent.svelte';

  let showForm = $state(false);
</script>

{#if showForm}
  <FormComponent onClose={() => showForm = false} />
{:else}
  <ListaComponent onAdd={() => showForm = true} />
{/if}
```

## Entity Layout (Complex with Subentity)

File: mod_risorse/ContattiLayout.svelte
```svelte
<script>
  import ListaComponent from './contatti/ListaComponent.svelte';
  import DettaglioLayout from './contatti/DettaglioLayout.svelte';

  let selectedId = $state(null);
</script>

{#if selectedId}
  <DettaglioLayout id={selectedId} onBack={() => selectedId = null} />
{:else}
  <ListaComponent onSelect={(id) => selectedId = id} />
{/if}
```

## Subentity Layout

File: mod_risorse/contatti/DettaglioLayout.svelte
```svelte
<script>
  import InfoComponent from './dettaglio/InfoComponent.svelte';
  import StoriaComponent from './dettaglio/StoriaComponent.svelte';
  import AzioniComponent from './dettaglio/AzioniComponent.svelte';

  export let id;
  export let onBack;

  let activeTab = $state('info');
</script>

<button onclick={onBack}>Indietro</button>

<nav>
  <button onclick={() => activeTab = 'info'}>Info</button>
  <button onclick={() => activeTab = 'storia'}>Storia</button>
  <button onclick={() => activeTab = 'azioni'}>Azioni</button>
</nav>

{#if activeTab === 'info'}
  <InfoComponent {id} />
{:else if activeTab === 'storia'}
  <StoriaComponent {id} />
{:else if activeTab === 'azioni'}
  <AzioniComponent {id} />
{/if}
```

## Component

File: mod_risorse/contatti/ListaComponent.svelte
```svelte
<script>
  import { contatti } from '../store.js';

  export let onSelect;
  export let onAdd;

  async function loadContatti() {
    const response = await fetch('/api/risorse/contatti');
    $contatti = await response.json();
  }
</script>

<button onclick={onAdd}>Nuovo Contatto</button>

{#each $contatti as contatto}
  <div onclick={() => onSelect(contatto.id)}>
    {contatto.nome}
  </div>
{/each}
```

## Store

File: mod_risorse/store.js
```javascript
import { writable } from 'svelte/store';

export const contatti = writable([]);
export const liste = writable([]);
export const campagne = writable([]);
export const loading = writable(false);
export const error = writable(null);
```

# SIMPLE MODULE EXAMPLE

```
mod_risorse/
├── Layout.svelte              # Entry point
├── ContattiLayout.svelte      # Entity layout
├── ListeLayout.svelte         # Entity layout
├── CampagneLayout.svelte      # Entity layout
├── store.js                   # Centralized store
├── contatti/
│   ├── ListaComponent.svelte
│   └── FormComponent.svelte
├── liste/
│   ├── ListaComponent.svelte
│   └── EditorComponent.svelte
└── campagne/
    ├── DashboardComponent.svelte
    └── ConfigComponent.svelte
```

# COMPLEX MODULE EXAMPLE

```
mod_risorse/
├── Layout.svelte
├── ContattiLayout.svelte
├── store.js
└── contatti/
    ├── ListaComponent.svelte
    ├── DettaglioLayout.svelte     # Subentity layout
    └── dettaglio/                  # Subentity folder
        ├── InfoComponent.svelte
        ├── StoriaComponent.svelte
        └── AzioniComponent.svelte
```

# IMPORT CHAIN

```
src/Layout.svelte
  └── import Layout from './mod_risorse/Layout.svelte'
        └── import ContattiLayout from './ContattiLayout.svelte'
              └── import ListaComponent from './contatti/ListaComponent.svelte'
              └── import DettaglioLayout from './contatti/DettaglioLayout.svelte'
                    └── import InfoComponent from './dettaglio/InfoComponent.svelte'
```
