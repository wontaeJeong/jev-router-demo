<script setup lang="ts">
defineProps<{ label: string; value: string; detail: string }>()
</script>

<template>
  <article class="decision-card">
    <div class="label mono">{{ label }}</div>
    <strong class="accent mono">{{ value }}</strong>
    <div class="muted">{{ detail }}</div>
  </article>
</template>
