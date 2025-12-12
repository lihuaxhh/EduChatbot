<template>
  <div class="page-wrap">
    <div class="toolbar card-soft" style="margin-bottom:12px;">
      <div class="toolbar-left">
        <h2 class="title-gradient-blue" style="margin:0;">练习</h2>
        <span style="margin-left:8px; color:#606266;">{{ index+1 }} / {{ questions.length }}</span>
      </div>
      <div class="toolbar-right">
        <el-button size="small" class="btn-outline" @click="prev" :disabled="index===0">上一题</el-button>
        <el-button size="small" class="btn-ghost" @click="next" :disabled="index>=questions.length-1">下一题</el-button>
      </div>
    </div>
    <div v-if="questions.length===0" style="color:#909399;">练习清单为空</div>
    <div v-else class="page-grid">
      <div class="mac-card soft-hover" style="padding:16px;">
        <LatexText :content="current.question" />
        <div class="divider-soft"></div>
        <el-input v-model="answer" type="textarea" :rows="4" placeholder="输入答案" />
        <div style="margin-top:12px; display:flex; gap:8px;">
          <el-button type="primary" @click="save">保存进度</el-button>
          <el-button @click="reveal">查看答案</el-button>
        </div>
        <el-collapse-transition>
          <div v-show="showAnswer" style="margin-top:10px; padding:10px; border:1px dashed var(--border-soft); border-radius:10px; background:#fff;">
            <strong>标准答案：</strong>
            <LatexText :content="current.answer" />
          </div>
        </el-collapse-transition>
      </div>
      <div class="aside-sticky">
        <div class="panel">
          <div class="panel-title">练习清单</div>
          <el-scrollbar height="420px">
            <div class="panel-list">
              <div
                v-for="(q, i) in questions"
                :key="q.id"
                class="panel-item"
                :style="i===index ? 'box-shadow: inset 0 0 0 2px var(--ring-soft);' : ''"
                @click="jump(i)"
              >
                <span>#{{ q.id }}</span>
                <el-tag size="small" :type="store.progress[q.id] ? 'success' : 'info'">
                  {{ store.progress[q.id] ? '已作答' : '未作答' }}
                </el-tag>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { usePracticeStore } from '../store'
import { getProblemById } from '../../../services/modules/problems'
import LatexText from '../../../components/LatexText.vue'
import { ElMessage } from 'element-plus'

const store = usePracticeStore()
const questions = ref<{id:number; question:string; answer:string}[]>([])
const index = ref(0)
const answer = ref('')
const showAnswer = ref(false)

const current = computed(() => questions.value[index.value] || { id:0, question:'', answer:'' })

onMounted(async () => {
  await store.init(1)
  for (const id of store.list) {
    try {
      const q = await getProblemById(id)
      questions.value.push({ id: q.id, question: q.question, answer: q.answer })
    } catch {}
  }
  loadProgress()
})

function loadProgress() {
  const cur = current.value
  answer.value = store.progress[cur.id] || ''
}
function prev() { if (index.value>0) { index.value--; showAnswer.value=false; loadProgress() } }
function next() { if (index.value<questions.value.length-1) { index.value++; showAnswer.value=false; loadProgress() } }
async function save() { const cur = current.value; await store.saveProgress(cur.id, answer.value); ElMessage.success('已保存') }
function reveal() { showAnswer.value = !showAnswer.value }
function jump(i:number){ index.value=i; showAnswer.value=false; loadProgress() }

function handleKey(e: KeyboardEvent){
  if (e.key === 'ArrowLeft') prev()
  else if (e.key === 'ArrowRight') next()
}
onMounted(() => window.addEventListener('keydown', handleKey))
onBeforeUnmount(() => window.removeEventListener('keydown', handleKey))
</script>
