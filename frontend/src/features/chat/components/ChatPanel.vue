<template>
  <div style="flex:1; display:flex; height:100vh;">
    <div style="flex:1; display:flex; flex-direction:column;">
      <div ref="list" style="flex:1; overflow:auto; padding:16px;">
        <div v-for="(m,i) in chat.messages" :key="i" style="margin-bottom:10px; display:flex;" :style="m.role==='user' ? 'justify-content:flex-end;' : 'justify-content:flex-start;'">
          <div :style="m.role==='user' ? userStyle : assistantStyle">
            {{ m.content }}
          </div>
        </div>
      </div>
      <div style="border-top:1px solid #eee; padding:12px; display:flex; gap:12px;">
        <el-input v-model="text" placeholder="输入消息" />
        <el-button type="primary" :loading="chat.loading" @click="send">发送</el-button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../store'
const chat = useChatStore()
const text = ref('')
const list = ref<HTMLDivElement|null>(null)
const userStyle = 'max-width:70%; background:#409eff; color:#fff; padding:10px; border-radius:10px 10px 0 10px; white-space:pre-wrap;'
const assistantStyle = 'max-width:70%; background:#f5f7fa; color:#303133; padding:10px; border-radius:10px 10px 10px 0; white-space:pre-wrap;'

async function send() {
  if (!text.value) return
  await chat.sendMessage(text.value)
  text.value = ''
}

watch(
  () => chat.messages.map(m => m.content).join('\n'),
  async () => {
    await nextTick()
    const el = list.value
    if (el) el.scrollTop = el.scrollHeight
  }
)
</script>
