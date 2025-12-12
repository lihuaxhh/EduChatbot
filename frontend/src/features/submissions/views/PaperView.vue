<template>
  <div class="page-wrap">
    <div class="toolbar card-soft" style="margin-bottom:12px;">
      <div class="toolbar-left">
        <h2 class="title-gradient-blue" style="margin:0;">学生作业</h2>
      </div>
      <div class="toolbar-right" style="color:#6b7280;">
        共 {{ questions.length }} 题
        <el-button type="primary" size="small" class="btn-ghost" @click="submit" :loading="submitting">提交作业</el-button>
      </div>
    </div>
    <div v-if="loading">加载中...</div>
    <div v-else class="page-grid">
      <div>
        <div
          v-for="(q, idx) in questions"
          :key="q.id"
          class="mac-card soft-hover"
          style="margin-bottom:16px; padding:16px;"
        >
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div style="font-weight:600; color:#334155;">第 {{ idx + 1 }} 题</div>
            <el-tag type="success" size="small">题号 {{ q.id }}</el-tag>
          </div>
          <div style="margin-bottom:12px; white-space:pre-wrap;">
            <LatexText :content="q.question" />
          </div>
          <div class="divider-soft"></div>
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <el-radio-group v-model="inputMethods[q.id]" size="small">
              <el-radio-button label="text">输入答案</el-radio-button>
              <el-radio-button label="image">上传图片</el-radio-button>
            </el-radio-group>
          </div>
          <div v-if="inputMethods[q.id] === 'text'">
            <el-input
              v-model="answers[q.id]"
              type="textarea"
              :rows="3"
              placeholder="请输入答案"
            />
          </div>
          <div v-else>
            <el-upload
              action=""
              :http-request="(opts) => handleImageUpload(opts, q.id)"
              :show-file-list="false"
              accept=".jpg,.jpeg,.png"
            >
              <el-button type="primary" size="small">选择图片</el-button>
            </el-upload>
            <div v-if="imagePreviews[q.id]" style="margin-top:10px;">
              <img :src="imagePreviews[q.id]" style="max-width:200px; border:1px solid var(--border-soft); padding:4px; border-radius:8px;" />
              <div style="font-size:12px; color:#666;">已上传</div>
            </div>
          </div>
        </div>
      </div>
      <div class="aside-sticky">
        <div class="panel">
          <div class="panel-title">作业概览</div>
          <div class="panel-list">
            <div class="panel-item">
              <span>题目数量</span><strong>{{ questions.length }}</strong>
            </div>
            <div class="panel-item">
              <span>已输入答案</span><strong>{{ answeredCount }}</strong>
            </div>
          </div>
          <div style="margin-top:12px;">
            <el-button type="primary" style="width:100%;" @click="submit" :loading="submitting">提交作业</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAssignmentPaper } from '../../../services/modules/assignments'
import { submitAssignment, uploadSubmissionImage } from '../../../services/modules/submissions'
import { ElMessage } from 'element-plus'
import LatexText from '../../../components/LatexText.vue'

const route = useRoute()
const router = useRouter()
const assignmentId = Number(route.params.id)

const loading = ref(false)
const submitting = ref(false)
const questions = ref<{id: number; question: string}[]>([])
const answers = ref<Record<number, string>>({})
const inputMethods = ref<Record<number, 'text' | 'image'>>({})
const imagePreviews = ref<Record<number, string>>({})
const answeredCount = ref(0)

onMounted(async () => {
  if (!assignmentId) return
  loading.value = true
  try {
    questions.value = await getAssignmentPaper(assignmentId)
    questions.value.forEach(q => {
      answers.value[q.id] = ''
      inputMethods.value[q.id] = 'text'
    })
    computeAnswered()
  } catch (e) {
    ElMessage.error('加载作业失败')
  } finally {
    loading.value = false
  }
})

function computeAnswered() {
  answeredCount.value = Object.values(answers.value).filter(v => (v || '').trim().length > 0).length
}

async function handleImageUpload(options: any, qid: number) {
    try {
        const res = await uploadSubmissionImage(options.file)
        // Store a special marker for image path
        answers.value[qid] = `[IMAGE]${res.path}`
        imagePreviews.value[qid] = `${import.meta.env.VITE_API_BASE_URL || ''}${res.url}`
        ElMessage.success('图片上传成功')
        computeAnswered()
    } catch(e) {
        ElMessage.error('上传失败')
    }
}

async function submit() {
  submitting.value = true
  try {
    const payload = {
      assignment_id: assignmentId,
      student_id: 1, // Hardcoded
      answers: Object.entries(answers.value).map(([qid, ans]) => ({
        question_id: Number(qid),
        student_answer: ans
      }))
    }
    await submitAssignment(payload)
    ElMessage.success('作业已提交，正在批改...')

    // 现实友好：轮询结果到达后再跳转（最多等待 10 秒）
    const start = Date.now()
    const poll = async () => {
      try {
        const res = await getSubmissionResults(assignmentId, 1)
        if (Array.isArray(res) && res.length > 0) {
          router.push(`/results/${assignmentId}`)
          return
        }
      } catch (_) {}
      if (Date.now() - start < 10000) {
        setTimeout(poll, 800)
      } else {
        // 超时仍然跳转，页面会自己请求并显示加载失败提示
        router.push(`/results/${assignmentId}`)
      }
    }
    poll()
    
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}
</script>
