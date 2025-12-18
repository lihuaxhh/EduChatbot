<template>
  <div style="flex:1; display:flex; height:100%;">
    <div style="flex:1; display:flex; flex-direction:column;">
      <div ref="list" id="chat-list" style="flex:1; overflow:auto; padding:16px; padding-bottom:96px;">
      <div v-for="(m,i) in chat.messages" :key="i" style="margin-bottom:10px; display:flex; gap:8px;" :style="m.role==='user' ? 'justify-content:flex-end;' : 'justify-content:flex-start;'">
        <el-avatar :size="28" :style="m.role==='user' ? 'background:#409eff;' : 'background:#67c23a;'">{{ m.role==='user' ? '我' : '助' }}</el-avatar>
        <div :style="m.role==='user' ? userStyle : assistantStyle">
          <div class="md" v-html="render(m.content)"></div>
          <div style="text-align:right; font-size:12px; color:#909399; margin-top:6px;">{{ now }}</div>
        </div>
      </div>
    </div>
      <div style="position:fixed; left:calc(var(--aside-w) + 24px); right:24px; bottom:0; border-top:1px solid var(--border-soft); padding:12px 18px; display:flex; gap:12px; background: var(--surface); backdrop-filter: blur(8px); box-shadow: 0 -6px 16px rgba(0,0,0,.06); border-top-left-radius: 16px; border-top-right-radius: 16px;">
        <el-input v-model="text" placeholder="输入消息" class="chat-input" />
        <el-button type="primary" :loading="chat.loading" @click="send">发送</el-button>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../store'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
// @ts-ignore
import renderMathInElement from 'katex/dist/contrib/auto-render.mjs'

const chat = useChatStore()
const props = defineProps<{
  initialMessage?: string
}>()
const text = ref('')
const list = ref<HTMLDivElement|null>(null)
const userStyle = 'max-width:70%; background:linear-gradient(135deg, #3b82f6, #2563EB); color:#fff; padding:10px; border-radius:10px 10px 0 10px; white-space:pre-wrap; box-shadow:0 6px 18px rgba(37,99,235,.18);'
const assistantStyle = 'max-width:70%; background:linear-gradient(135deg, #f8fafc, #eef2ff); color:#303133; padding:10px; border-radius:10px 10px 10px 0; box-shadow:0 6px 18px rgba(0,0,0,.08);'
const now = new Date().toLocaleTimeString()

marked.setOptions({ gfm: true, breaks: true })
function render(t: string) {
  let s = (t || '')
    // 将单反斜杠行尾换行转为 LaTeX 的 \\ 换行
    .replace(/(?<!\\)\\\s*$/gm, '\\\\')
    // 统一一些常见错误空格：\sin alpha -> \sin\alpha
    .replace(/\\(sin|cos|tan|cot|sec|csc)\s+([a-zA-Z]+)/g, '\\$1\\$2')
    // \vec a -> \vec{a}
    .replace(/\\vec\s+([a-zA-Z])/g, '\\vec{$1}')
    // 将 $$ 换行块（$$<CRLF>...<CRLF>$$）统一为 \\[ ... \\]
    .replace(/(^|\r?\n)\s*\$\$\s*(?:\r?\n)([\s\S]*?)(?:\r?\n)\s*\$\$(?=\r?\n|$)/g, '$1\\\\[$2\\\\]')
    // 将 [ ... ] 包裹的 LaTeX 块转为 \[ ... \]（仅当包含对齐/分段环境）
    .replace(/\[\s*([\s\S]*?\\begin\{(?:aligned|cases)\}[\s\S]*?\\end\{(?:aligned|cases)\}[\s\S]*?)\s*\]/g, '\\[$1\\]')
    // 去除无意义的 \x、\y（常见误写）
    .replace(/\\([xy])\b/g, '$1')

  // 保护 LaTeX 公式不被 marked 解析（占位使用安全的自定义标签，避免被 Markdown 语法改写）
  const mathBlocks: string[] = []
  const protect = (regex: RegExp) => {
    s = s.replace(regex, (match) => {
      mathBlocks.push(match)
      const i = mathBlocks.length - 1
      return `<math-block data-i="${i}"></math-block>`
    })
  }

  // 注意顺序：先长后短，先块后行
  protect(/\\\[([\s\S]*?)\\\]/g)
  protect(/\$\$([\s\S]*?)\$\$/g)
  protect(/\\\(([\s\S]*?)\\\)/g)
  protect(/\$([^\n$]+)\$/g)

  const html = marked.parse(s) as string
  
  // 还原 LaTeX 公式
  const restoredHtml = html.replace(/<math-block[^>]*data-i="(\d+)"[^>]*><\/math-block>/g, (_m, index) => {
    const i = parseInt(index)
    return mathBlocks[i] || ''
  })

  // 延时渲染，确保 DOM 已更新
  setTimeout(() => {
    const el = document.getElementById('chat-list')
    if (el) {
      renderMathInElement(el, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\[', right: '\\]', display: true },
          { left: '\\(', right: '\\)', display: false },
          { left: '$', right: '$', display: false }
        ],
        throwOnError: false
      })
    }
  }, 0)

  return DOMPurify.sanitize(restoredHtml)
}

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
    
    // 使用导入的 renderMathInElement
    el?.querySelectorAll('.md').forEach(e => {
      renderMathInElement(e as HTMLElement, { delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\[', right: '\\]', display: true},
        {left: '\\(', right: '\\)', display: false}
      ], throwOnError: false })
    })
  }
)
</script>

<style scoped>
.chat-input .el-input__wrapper { background: var(--surface); border: 1px solid var(--border-soft); box-shadow: none; }
.chat-input .el-input__inner { font-weight: 500; }
.md :deep(code) { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
.md :deep(pre code) { display: block; padding: 12px; overflow: auto; }
</style>
