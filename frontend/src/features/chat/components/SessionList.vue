<template>
  <div style="width:300px; border-right:1px solid #eee; height:100vh; display:flex; flex-direction:column;">
    <div style="padding:12px; display:flex; align-items:center; justify-content:space-between;">
      <div style="font-weight:600;">会话</div>
      <el-button type="primary" size="small" @click="newChat">新对话</el-button>
    </div>
    <div style="flex:1; overflow:auto;">
      <div
        v-for="s in chat.sessions"
        :key="s.session_id"
        :style="s.session_id===chat.activeSessionId? 'padding:12px; background:#f5f7fa; cursor:pointer;' : 'padding:12px; cursor:pointer;'"
        @click="select(s.session_id)"
      >
        <div style="font-weight:500;">{{ s.title || '未命名会话' }}</div>
        <div style="font-size:12px; color:#909399; margin-top:4px;">{{ s.updated_at }}</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useChatStore } from '../store'
const chat = useChatStore()
function select(id: string) { chat.selectSession(id) }
async function newChat() { await chat.newSession() }
</script>
