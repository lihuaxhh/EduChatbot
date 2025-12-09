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
        class="session-item"
        :class="{ active: s.session_id === chat.activeSessionId }"
        @click="select(s.session_id)"
      >
        <div style="display:flex; justify-content:space-between; align-items:start;">
            <div style="font-weight:500; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{{ s.title || '未命名会话' }}</div>
            <el-button link type="danger" size="small" @click.stop="remove(s.session_id)">删除</el-button>
        </div>
        <div style="font-size:12px; color:#909399; margin-top:4px;">{{ formatTime(s.updated_at) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '../store'
import { ElMessageBox } from 'element-plus'

const chat = useChatStore()

function select(id: string) { chat.selectSession(id) }
async function newChat() { await chat.newSession() }

async function remove(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该会话吗？', '提示', { type: 'warning' })
    await chat.removeSession(id)
  } catch {
    // cancelled
  }
}

function formatTime(iso: string) {
    if (!iso) return ''
    return new Date(iso).toLocaleString()
}
</script>

<style scoped>
.session-item {
    padding: 12px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
}
.session-item:hover {
    background-color: #fafafa;
}
.session-item.active {
    background-color: #f0f7ff;
    border-left: 3px solid #409eff;
}
</style>
