# Vue 安全编码规范

> **版本**：V1.0 &nbsp;|&nbsp; **适用范围**：所有基于 Vue 2/3 开发的前端项目
> **级别定义**：【规则】必须遵守的强制约定 ·【建议】应加以考虑的推荐约定

---

## 1 组件设计

### 1.1 【规则】组件名必须使用多单词

避免与 HTML 原生元素冲突。

```vue
<!-- ✗ 错误 -->
<script>
export default { name: 'Todo' }
</script>

<!-- ✓ 正确 -->
<script>
export default { name: 'TodoItem' }
</script>
```

### 1.2 【规则】Props 必须定义类型和验证

```vue
<!-- ✗ 错误 -->
<script>
defineProps(['status'])
</script>

<!-- ✓ 正确 -->
<script setup>
defineProps({
  status: {
    type: String,
    required: true,
    validator: (v) => ['active', 'inactive'].includes(v)
  }
})
</script>
```

### 1.3 【规则】禁止直接修改 Props

Props 是单向数据流，子组件不得直接修改。须通过 `emit` 事件通知父组件。

### 1.4 【规则】组件文件名使用 PascalCase

```
✗ mycomponent.vue
✓ MyComponent.vue
```

---

## 2 Composition API

### 2.1 【规则】响应式状态须使用 `ref` 或 `reactive`

```js
// ✗ 错误：非响应式
let count = 0

// ✓ 正确
const count = ref(0)
```

### 2.2 【规则】计算属性禁止产生副作用

`computed` 仅用于派生状态，不得在其中修改其他响应式数据或执行异步操作。

### 2.3 【规则】`watch` 须在组件卸载时清理

```js
const stop = watch(source, callback)
onUnmounted(() => stop())
```

### 2.4 【建议】优先使用 `watchEffect` 自动追踪依赖

当依赖关系明确时用 `watch`，依赖复杂时用 `watchEffect` 自动收集。

---

## 3 生命周期

### 3.1 【规则】定时器、事件监听须在 `onUnmounted` 中清理

```js
onMounted(() => {
  const timer = setInterval(poll, 5000)
  window.addEventListener('resize', onResize)
  onUnmounted(() => {
    clearInterval(timer)
    window.removeEventListener('resize', onResize)
  })
})
```

### 3.2 【规则】异步操作须处理组件已卸载的情况

```js
onMounted(async () => {
  const data = await fetchData()
  if (isMounted.value) {
    state.value = data
  }
})
```

---

## 4 模板与渲染

### 4.1 【规则】禁止 `v-for` 和 `v-if` 同时用在同一元素上

`v-for` 优先级高于 `v-if`，会导致每次渲染都遍历整个列表。

```vue
<!-- ✗ 错误 -->
<li v-for="user in users" v-if="user.active" :key="user.id">

<!-- ✓ 正确：先过滤 -->
<li v-for="user in activeUsers" :key="user.id">
```

### 4.2 【规则】`v-for` 必须提供唯一 `key`

禁止使用 `index` 作为 `key`（列表会增删时）。

### 4.3 【规则】复杂逻辑须提取为计算属性或方法

模板中禁止出现超过一行的表达式。

---

## 5 安全

### 5.1 【规则】禁止对用户输入使用 `v-html`

`v-html` 直接渲染 HTML，存在 XSS 风险。

```vue
<!-- ✗ 错误 -->
<div v-html="userInput"></div>

<!-- ✓ 正确：使用文本插值 -->
<div>{{ userInput }}</div>
```

### 5.2 【规则】动态 URL 须验证协议

防止 `javascript:` 协议注入。

```js
function sanitizeUrl(url) {
  const parsed = new URL(url)
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return '#'
  }
  return url
}
```

### 5.3 【规则】禁止在模板中拼接用户输入到事件处理器

---

## 6 性能

### 6.1 【建议】大型列表使用虚拟滚动

超过 1000 条数据的列表须使用 `vue-virtual-scroller` 等虚拟滚动方案。

### 6.2 【建议】路由组件使用懒加载

```js
const UserProfile = () => import('./views/UserProfile.vue')
```

### 6.3 【建议】频繁切换用 `v-show`，条件渲染用 `v-if`

### 6.4 【建议】大型组件使用 `defineAsyncComponent` 异步加载

---

## 7 状态管理

### 7.1 【规则】全局状态须使用 Pinia/Vuex，禁止滥用 `provide/inject`

### 7.2 【规则】Store 中的异步操作须有错误处理

### 7.3 【建议】Store 按功能模块拆分，避免单一巨型 Store

---

## 8 工程化

### 8.1 【规则】代码提交前须通过以下工具检查

| 工具 | 用途 |
|------|------|
| `eslint` + `eslint-plugin-vue` | Vue 代码规范检查 |
| `prettier` | 代码格式化 |
| `vue-tsc` | TypeScript 类型检查 |

### 8.2 【规则】单文件组件顺序：`<script>` → `<template>` → `<style>`

### 8.3 【规则】`<style>` 须使用 `scoped` 或 CSS Modules 避免样式污染

---

## 参考文献

- Vue.js Style Guide (https://vuejs.org/style-guide/)
- Vue.js Security (https://vuejs.org/guide/best-practices/security.html)
