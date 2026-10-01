<script setup lang="ts">
withDefaults(defineProps<{ label: string; detail: string; value?: string }>(), {
  value: 'LIVE',
})
</script>

<template>
  <article class="metric-card" :class="{ unavailable: value === 'N/A' }">
    <div class="label">{{ label }}</div>
    <strong>{{ value }}</strong>
    <div class="muted">{{ detail }}</div>
  </article>
</template>
