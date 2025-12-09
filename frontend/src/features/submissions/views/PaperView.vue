<template>
  <div style="padding:20px; max-width:800px; margin:0 auto;">
    <h2>学生作业</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <div v-for="(q, idx) in questions" :key="q.id" style="margin-bottom:24px; padding:16px; border:1px solid #eee; border-radius:8px;">
        <div style="margin-bottom:12px; font-weight:bold;">第 {{ idx + 1 }} 题</div>
        <div style="margin-bottom:12px; white-space:pre-wrap;">
             <LatexText :content="q.question" />
        </div>
        
        <div style="margin-bottom:12px;">
            <el-radio-group v-model="inputMethods[q.id]">
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
                <el-button type="primary">选择图片</el-button>
            </el-upload>
            <div v-if="imagePreviews[q.id]" style="margin-top:10px;">
                <img :src="imagePreviews[q.id]" style="max-width:200px; border:1px solid #ddd; padding:4px;" />
                <div style="font-size:12px; color:#666;">已上传</div>
            </div>
        </div>
      </div>
      <div style="margin-top:20px; text-align:center;">
        <el-button type="primary" size="large" @click="submit" :loading="submitting">提交作业</el-button>
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

onMounted(async () => {
  if (!assignmentId) return
  loading.value = true
  try {
    questions.value = await getAssignmentPaper(assignmentId)
    questions.value.forEach(q => {
      answers.value[q.id] = ''
      inputMethods.value[q.id] = 'text'
    })
  } catch (e) {
    ElMessage.error('加载作业失败')
  } finally {
    loading.value = false
  }
})

async function handleImageUpload(options: any, qid: number) {
    try {
        const res = await uploadSubmissionImage(options.file)
        // Store a special marker for image path
        answers.value[qid] = `[IMAGE]${res.path}`
        imagePreviews.value[qid] = `${import.meta.env.VITE_API_BASE_URL || ''}${res.url}`
        ElMessage.success('图片上传成功')
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
    ElMessage.success('作业已提交，后台批改中')
    
    // Redirect to results page immediately or after delay
    // For now, let's go to results view
    // Note: In real world, might need to wait or show pending state.
    // The user requirement says "Teacher can see result quickly, student sees uploaded".
    // But user also mentioned "Student knows which one is wrong -> recommendation".
    // So let's redirect to result view.
    setTimeout(() => {
        router.push(`/results/${assignmentId}`)
    }, 1000)
    
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}
</script>
