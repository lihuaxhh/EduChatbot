<template>
  <div class="page-wrap">
    <div class="toolbar card-soft" style="margin-bottom:12px;">
      <div class="toolbar-left">
        <h2 class="title-gradient-violet" style="margin:0;">Wrongbook</h2>
      </div>
      <div class="toolbar-right">
        <el-select v-model="groupBy" style="width:200px;">
          <el-option label="By Time" value="time" />
          <el-option label="By Difficulty" value="difficulty" />
          <el-option label="By Function Type" value="type" />
          <el-option label="By Property" value="property" />
        </el-select>
        <el-button class="btn-outline" @click="fetch">Refresh</el-button>
      </div>
    </div>
    <div class="mac-card table-compact" style="padding:12px;">
      <el-table :data="items" stripe style="width:100%;">
        <el-table-column prop="question_id" label="Question ID" width="100" />
        <el-table-column label="Stem">
          <template #default="scope">
            <LatexText :content="scope.row.question" />
          </template>
        </el-table-column>
        <el-table-column label="My Wrong Answer" width="240">
          <template #default="scope">
            <LatexText :content="scope.row.student_answer" />
          </template>
        </el-table-column>
        <el-table-column prop="error_count" label="Error Count" width="120" />
        <el-table-column prop="last_error_time" label="Last Error Time" width="180" />
        <el-table-column label="Action" width="220">
          <template #default="scope">
            <el-button size="small" type="primary" @click="redo(scope.row.question_id)">Redo</el-button>
            <el-button size="small" style="margin-left:6px;" @click="remove(scope.row.question_id)">Remove</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex; justify-content:flex-end; margin-top:8px;">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="items.length"
          :page-size="10"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getWrongbook } from '../../../services/modules/wrongbook'
import { usePracticeStore } from '../../practice/store'
import LatexText from '../../../components/LatexText.vue'
import { ElMessage } from 'element-plus'

const studentId = 1
const groupBy = ref('time')
const items = ref<any[]>([])
const store = usePracticeStore()

onMounted(async () => {
  await store.init(studentId)
  fetch()
})

async function fetch() {
  try {
    items.value = await getWrongbook(studentId, groupBy.value)
  } catch { ElMessage.error('Failed to load') }
}
async function redo(qid: number) { await store.add(qid); ElMessage.success('Added to practice list'); }
function remove(qid: number) { items.value = items.value.filter(i => i.question_id !== qid) }
</script>
