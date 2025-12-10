<template>
  <div ref="el" class="latex-content"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{ content: string }>()
const el = ref<HTMLDivElement | null>(null)

function render() {
  if (!el.value) return
  const raw = props.content || ''
  const normalized = raw.replace(/\\\\/g, '\\')
  el.value.innerHTML = normalized
  // @ts-ignore
  if (window.renderMathInElement) {
    // @ts-ignore
    window.renderMathInElement(el.value, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false }
      ],
      throwOnError: false
    })
  }
}

onMounted(render)
watch(() => props.content, render)
</script>

<style scoped>
.latex-content {
  display: inline-block;
}
</style>
