<template>
  <div style="display:flex;">
    <SessionList />
    <ChatPanel />
  </div>
</template>
<script setup lang="ts">
import SessionList from '../components/SessionList.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { useChatStore } from '../store'
import { onMounted } from 'vue'
const chat = useChatStore()
onMounted(() => { chat.loadSessions() })
</script>
