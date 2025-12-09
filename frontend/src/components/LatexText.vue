<template>
  <div ref="el" class="latex-content"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{ content: string }>()
const el = ref<HTMLDivElement | null>(null)

function render() {
  if (!el.value) return
  // @ts-ignore
  if (window.katex) {
    // @ts-ignore
    window.katex.render(props.content || '', el.value, {
      throwOnError: false,
      displayMode: false // Inline by default, or maybe check if it contains block math
    })
  } else {
    el.value.innerText = props.content || ''
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
