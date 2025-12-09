<template>
  <div style="padding:16px;">
    <el-upload action="" :http-request="customRequest" accept=".csv,.xlsx,.xls,.json">
      <el-button type="primary">上传题目文件</el-button>
    </el-upload>
    <div style="margin-top:12px;">{{ status }}</div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'

const status = ref('')

async function customRequest(options: any) {
  const form = new FormData()
  form.append('file', options.file as File)
  const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/problems/upload`, {
    method: 'POST', body: form
  })
  status.value = String(resp.status)
}
</script>
