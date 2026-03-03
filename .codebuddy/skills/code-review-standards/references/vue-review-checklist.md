# Vue Code Review Checklist

Comprehensive checklist for reviewing Vue.js code, covering Vue 2/3, Composition API, best practices, and common pitfalls.

## Component Design

### 1. Component Naming
```vue
<!-- ❌ WRONG - Single word component name -->
<template>
  <button>Click</button>
</template>
<script>
export default {
  name: 'Button' // Conflicts with HTML element
}
</script>

<!-- ✅ CORRECT - Multi-word component name -->
<template>
  <button>Click</button>
</template>
<script>
export default {
  name: 'AppButton' // Clear, no conflicts
}
</script>
```

### 2. Props Definition
```vue
<script>
// ❌ WRONG - Array syntax, no validation
export default {
  props: ['title', 'count', 'isActive']
}

// ✅ CORRECT - Object syntax with validation
export default {
  props: {
    title: {
      type: String,
      required: true,
      validator: (value) => value.length > 0
    },
    count: {
      type: Number,
      default: 0
    },
    isActive: {
      type: Boolean,
      default: false
    }
  }
}
</script>
```

### 3. Props Mutation
```vue
<script>
// ❌ WRONG - Mutating props directly
export default {
  props: ['value'],
  methods: {
    updateValue() {
      this.value = 'new value' // Vue warning!
    }
  }
}

// ✅ CORRECT - Emit event to parent
export default {
  props: ['value'],
  emits: ['update:value'],
  methods: {
    updateValue() {
      this.$emit('update:value', 'new value')
    }
  }
}

// ✅ CORRECT - Use local data copy
export default {
  props: ['initialValue'],
  data() {
    return {
      localValue: this.initialValue
    }
  }
}
</script>
```

## Composition API (Vue 3)

### 1. Reactive State
```vue
<script setup>
import { ref, reactive } from 'vue'

// ❌ WRONG - Losing reactivity
let count = 0 // Not reactive
const user = { name: 'John' } // Not reactive

// ✅ CORRECT - Using ref for primitives
const count = ref(0)
count.value++ // Access via .value

// ✅ CORRECT - Using reactive for objects
const user = reactive({
  name: 'John',
  age: 30
})
user.name = 'Jane' // Direct access
</script>
```

### 2. Computed Properties
```vue
<script setup>
import { ref, computed } from 'vue'

const items = ref([1, 2, 3, 4, 5])

// ❌ WRONG - Side effects in computed
const total = computed(() => {
  console.log('Computing...') // Side effect
  localStorage.setItem('total', sum) // Side effect
  return items.value.reduce((a, b) => a + b, 0)
})

// ✅ CORRECT - Pure computed
const total = computed(() => {
  return items.value.reduce((a, b) => a + b, 0)
})

// ✅ CORRECT - Writable computed
const fullName = computed({
  get() {
    return `${firstName.value} ${lastName.value}`
  },
  set(newValue) {
    [firstName.value, lastName.value] = newValue.split(' ')
  }
})
</script>
```

### 3. Watch vs WatchEffect
```vue
<script setup>
import { ref, watch, watchEffect } from 'vue'

const searchQuery = ref('')
const userId = ref(1)

// ❌ WRONG - watchEffect when watch is better
watchEffect(() => {
  if (userId.value) {
    fetchUser(userId.value)
  }
})

// ✅ CORRECT - watch for specific dependencies
watch(userId, (newId, oldId) => {
  fetchUser(newId)
}, { immediate: true })

// ✅ CORRECT - watchEffect for multiple reactive deps
watchEffect(() => {
  // Automatically tracks searchQuery and filters
  const results = filterItems(searchQuery.value, filters.value)
  displayResults(results)
})

// ✅ CORRECT - Cleanup in watch
watch(userId, async (newId, oldId, onCleanup) => {
  const controller = new AbortController()
  onCleanup(() => controller.abort())

  const user = await fetchUser(newId, { signal: controller.signal })
  userData.value = user
})
</script>
```

## Lifecycle Hooks

### 1. Cleanup Resources
```vue
<script setup>
import { onMounted, onUnmounted } from 'vue'

// ❌ WRONG - Memory leak, no cleanup
onMounted(() => {
  window.addEventListener('resize', handleResize)
  setInterval(pollData, 5000)
})

// ✅ CORRECT - Proper cleanup
let intervalId = null

onMounted(() => {
  window.addEventListener('resize', handleResize)
  intervalId = setInterval(pollData, 5000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (intervalId) clearInterval(intervalId)
})
</script>
```

### 2. Async Operations
```vue
<script setup>
import { ref, onMounted } from 'vue'

const data = ref(null)
const loading = ref(false)
const error = ref(null)

// ❌ WRONG - No error handling, no loading state
onMounted(async () => {
  data.value = await fetchData()
})

// ✅ CORRECT - Proper async handling
onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    data.value = await fetchData()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>
```

## Performance

### 1. v-for with v-if
```vue
<!-- ❌ WRONG - v-if with v-for on same element -->
<template>
  <ul>
    <li v-for="user in users" v-if="user.isActive" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>

<!-- ✅ CORRECT - Use computed property -->
<template>
  <ul>
    <li v-for="user in activeUsers" :key="user.id">
      {{ user.name }}
    </li>
  </ul>
</template>

<script setup>
import { computed } from 'vue'

const activeUsers = computed(() =>
  users.value.filter(user => user.isActive)
)
</script>
```

### 2. Key Attribute
```vue
<!-- ❌ WRONG - Using index as key -->
<template>
  <div v-for="(item, index) in items" :key="index">
    {{ item.name }}
  </div>
</template>

<!-- ✅ CORRECT - Using unique identifier -->
<template>
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

### 3. Component Lazy Loading
```javascript
// ❌ WRONG - Eager loading all components
import HeavyComponent from './HeavyComponent.vue'
import AnotherHeavy from './AnotherHeavy.vue'

// ✅ CORRECT - Lazy loading
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)

// ✅ CORRECT - With loading/error states
const HeavyComponent = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 3000
})
```

## Security

### 1. XSS Prevention
```vue
<!-- ❌ WRONG - XSS vulnerability -->
<template>
  <div v-html="userInput"></div>
</template>

<!-- ✅ CORRECT - Text interpolation (auto-escaped) -->
<template>
  <div>{{ userInput }}</div>
</template>

<!-- ✅ CORRECT - Sanitize if HTML needed -->
<template>
  <div v-html="sanitizedHtml"></div>
</template>

<script setup>
import DOMPurify from 'dompurify'

const sanitizedHtml = computed(() =>
  DOMPurify.sanitize(userInput.value)
)
</script>
```

### 2. URL Injection
```vue
<!-- ❌ WRONG - Potential javascript: URL -->
<template>
  <a :href="userUrl">Link</a>
</template>

<!-- ✅ CORRECT - Validate URL -->
<script setup>
const safeUrl = computed(() => {
  try {
    const url = new URL(userUrl.value)
    if (['http:', 'https:'].includes(url.protocol)) {
      return url.href
    }
  } catch {}
  return '#'
})
</script>
```

## Template Best Practices

### 1. Complex Logic in Templates
```vue
<!-- ❌ WRONG - Complex logic in template -->
<template>
  <div>
    {{ items.filter(i => i.active).map(i => i.name).join(', ') }}
  </div>
</template>

<!-- ✅ CORRECT - Use computed -->
<template>
  <div>{{ activeItemNames }}</div>
</template>

<script setup>
const activeItemNames = computed(() =>
  items.value.filter(i => i.active).map(i => i.name).join(', ')
)
</script>
```

### 2. Event Handlers
```vue
<!-- ❌ WRONG - Inline complex logic -->
<template>
  <button @click="count++; if(count > 10) reset(); logClick()">
    Click
  </button>
</template>

<!-- ✅ CORRECT - Method reference -->
<template>
  <button @click="handleClick">Click</button>
</template>

<script setup>
const handleClick = () => {
  count.value++
  if (count.value > 10) reset()
  logClick()
}
</script>
```

## State Management (Pinia)

### 1. Store Definition
```javascript
// ❌ WRONG - Mutating state directly outside store
store.items.push(newItem)

// ✅ CORRECT - Use actions
// stores/items.js
export const useItemsStore = defineStore('items', {
  state: () => ({
    items: []
  }),
  actions: {
    addItem(item) {
      this.items.push(item)
    }
  }
})
```

### 2. Composable Stores
```javascript
// ✅ CORRECT - Composition API style store
export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  async function login(credentials) {
    user.value = await authApi.login(credentials)
  }

  function logout() {
    user.value = null
  }

  return { user, isLoggedIn, login, logout }
})
```

## Testing

### 1. Component Testing
```javascript
import { mount } from '@vue/test-utils'
import MyComponent from './MyComponent.vue'

// ✅ CORRECT - Proper component test
describe('MyComponent', () => {
  it('renders props correctly', () => {
    const wrapper = mount(MyComponent, {
      props: { title: 'Hello' }
    })
    expect(wrapper.text()).toContain('Hello')
  })

  it('emits event on click', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
  })
})
```

## Static Analysis Tools

Recommended tools:
- **ESLint**: eslint-plugin-vue for Vue-specific rules
- **Vetur/Volar**: IDE support and type checking
- **Vue DevTools**: Runtime debugging
- **Vitest**: Unit testing framework

Configuration example (.eslintrc.js):
```javascript
module.exports = {
  extends: [
    'plugin:vue/vue3-recommended',
    '@vue/typescript/recommended'
  ],
  rules: {
    'vue/multi-word-component-names': 'error',
    'vue/no-v-html': 'warn',
    'vue/require-default-prop': 'error'
  }
}
```
