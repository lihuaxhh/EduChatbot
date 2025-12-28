<template>
  <div style="padding:16px;">
    <el-upload action="" :http-request="customRequest" accept=".png,.jpg,.jpeg">
      <el-button type="primary">Upload Answer Image</el-button>
    </el-upload>
    <div style="margin-top:12px; white-space:pre-wrap;">{{ text }}</div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'

const text = ref('')

async function customRequest(options: any) {
  const form = new FormData()
  form.append('file', options.file as File)
  const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/submissions/ocr`, {
    method: 'POST', body: form
  })
  const data = await resp.json()
  text.value = String(data.text || '')
}
</script>
