<template>
  <div class="page-wrap">
    <div class="toolbar card-soft" style="margin-bottom:12px;">
      <div class="toolbar-left">
        <h2 class="title-gradient-blue" style="margin:0;">Notifications</h2>
      </div>
      <div class="toolbar-right">
        <el-button size="small" class="btn-outline" @click="refresh">Refresh</el-button>
        <el-button size="small" type="primary" @click="readAll">Mark All as Read</el-button>
      </div>
    </div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="items.length===0" class="card-soft" style="padding:24px; color:#909399;">No notifications</div>
    <el-scrollbar v-else height="calc(100vh - 180px)">
      <div style="display:flex; flex-direction:column; gap:10px;">
        <div v-for="n in items" :key="n.id" class="mac-card soft-hover" style="padding:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:8px;">
              <el-tag :type="n.is_read ? 'info' : 'success'" size="small">{{ n.is_read ? 'Read' : 'Unread' }}</el-tag>
              <strong>{{ n.title }}</strong>
              <small style="color:#6b7280;">{{ formatTime(n.created_at) }}</small>
            </div>
            <el-button size="small" @click="readOne(n)" :disabled="n.is_read">Mark as Read</el-button>
          </div>
          <div style="margin-top:8px; color:#374151; white-space:pre-wrap;">{{ n.content }}</div>
        </div>
      </div>
    </el-scrollbar>
  </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import dayjs from 'dayjs'
  import { listNotifications, markRead, markAllRead, type NotificationItem } from '../../../services/modules/notifications'
  import { ElMessage } from 'element-plus'
  
  const loading = ref(false)
  const items = ref<NotificationItem[]>([])
  
  async function refresh() {
    loading.value = true
    try {
      items.value = await listNotifications()
    } catch {
      ElMessage.error('Failed to load notifications')
    } finally {
      loading.value = false
    }
  }
  
  async function readOne(n: NotificationItem) {
    try {
      await markRead(n.id)
      n.is_read = true
    } catch {}
  }
  
  async function readAll() {
    try {
      await markAllRead()
      items.value = items.value.map(i => ({ ...i, is_read: true }))
    } catch {}
  }
  
  function formatTime(t: string) {
    return dayjs(t).format('YYYY-MM-DD HH:mm')
  }
  
  onMounted(refresh)
  </script>
  
  <style scoped>
  </style>
  
