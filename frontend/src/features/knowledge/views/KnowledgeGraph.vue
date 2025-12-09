<template>
  <div style="padding:16px;">
    <el-input v-model="center" placeholder="中心节点" style="max-width:320px" />
    <el-button type="primary" @click="load">加载</el-button>
    <pre style="margin-top:12px; white-space:pre-wrap;">{{ json }}</pre>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'

const center = ref('')
const json = ref('')

async function load() {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/knowledge-graph?center=${encodeURIComponent(center.value)}`)
  const data = await resp.json()
  json.value = JSON.stringify(data)
}
</script>
