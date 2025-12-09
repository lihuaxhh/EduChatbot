<template>
  <div style="padding:20px; max-width:800px; margin:0 auto;">
    <h2>批改结果</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <div v-for="(res, idx) in results" :key="idx" 
           style="margin-bottom:24px; padding:16px; border:1px solid #eee; border-radius:8px;"
           :style="{ borderColor: res.is_correct ? '#67c23a' : '#f56c6c', backgroundColor: res.is_correct ? '#f0f9eb' : '#fef0f0' }"
      >
        <div style="margin-bottom:12px; font-weight:bold;">第 {{ idx + 1 }} 题</div>
        <div style="margin-bottom:8px;">
            <strong>学生答案：</strong>
            <div v-if="res.student_answer.includes('[IMAGE]')">
                <img :src="getImageUrl(res.student_answer)" style="max-width:300px; border:1px solid #ddd; margin: 5px 0;" />
                <div v-if="res.student_answer.includes('[OCR]:')">
                    <small>OCR识别内容: {{ res.student_answer.split('[OCR]:')[1] }}</small>
                </div>
            </div>
            <div v-else>{{ res.student_answer }}</div>
        </div>
        
        <div style="margin-top:12px; border-top:1px dashed #ccc; padding-top:12px;">
            <div v-if="res.is_correct" style="color:#67c23a; font-weight:bold;">
                <el-icon><Check /></el-icon> 回答正确
            </div>
            <div v-else>
                <div style="color:#f56c6c; font-weight:bold; margin-bottom:4px;">
                    <el-icon><Close /></el-icon> 回答错误
                </div>
                <div v-if="res.error_type" style="margin-bottom:4px;">
                    <el-tag type="danger" size="small">{{ formatErrorType(res.error_type) }}</el-tag>
                </div>
                <div v-if="res.analysis" style="color:#606266; font-size:14px; line-height:1.5;">
                    <strong>分析建议：</strong>
                    <LatexText :content="res.analysis" />
                </div>
            </div>
        </div>
      </div>
      
      <div style="text-align:center; margin-top:20px;">
        <el-button @click="router.push('/problems')">返回题库</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSubmissionResults, type SubmissionResult } from '../../../services/modules/submissions'
import { Check, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import LatexText from '../../../components/LatexText.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.params.assignmentId)
const studentId = Number(route.params.studentId) || 1 // Hardcoded default

const loading = ref(false)
const results = ref<SubmissionResult[]>([])

onMounted(async () => {
  if (!assignmentId) return
  loading.value = true
  try {
    results.value = await getSubmissionResults(assignmentId, studentId)
  } catch (e) {
    ElMessage.error('加载结果失败')
  } finally {
    loading.value = false
  }
})

function getImageUrl(answer: string) {
    const path = answer.split('\n')[0].replace('[IMAGE]', '')
    return `${import.meta.env.VITE_API_BASE_URL || ''}/${path}`
}

function formatErrorType(type: string) {
    const map: Record<string, string> = {
        'knowledge': '知识点错误',
        'calculation': '计算错误',
        'misreading': '审题错误',
        'logic': '逻辑错误',
        'method': '方法错误'
    }
    return map[type] || type
}
</script>
