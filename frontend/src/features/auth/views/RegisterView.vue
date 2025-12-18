<template>
  <div class="auth-wrapper">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
    
    <div class="auth-card glass-panel split-layout">
      <!-- Left Panel: Branding -->
      <div class="left-panel">
        <div class="brand-content">
          <div class="logo-area">
            <h1 class="brand-title">EduChatbot</h1>
          </div>
          <h2 class="welcome-title">加入我们<br>共创未来</h2>
          <p class="brand-desc">
            注册账号，立即体验智能辅助教学与个性化学习推荐系统。我们致力于通过技术创新，让每一次学习都更高效，让每一位师生都能享受科技带来的便利。
          </p>
          
          <div class="quote-box">
            <p class="quote-text">"教育的本质意味着：一棵树摇动另一棵树，一朵云推动另一朵云，一个灵魂唤醒另一个灵魂。"</p>
            <p class="quote-author">— 雅斯贝尔斯</p>
          </div>
        </div>
        <div class="panel-bg-overlay"></div>
      </div>

      <!-- Right Panel: Form -->
      <div class="right-panel">
        <div class="form-container">
          <div class="form-header">
            <h3>创建账号</h3>
            <p class="subtitle">请填写以下信息完成注册</p>
          </div>
          
          <el-form ref="formRef" :model="form" :rules="rules" class="auth-form" size="large">
            
            <div class="role-selector-mini">
              <div 
                class="role-btn" 
                :class="{ active: form.role === 'student' }"
                @click="form.role = 'student'"
              >
                <el-icon><User /></el-icon> 我是学生
              </div>
              <div 
                class="role-btn" 
                :class="{ active: form.role === 'teacher' }"
                @click="form.role = 'teacher'"
              >
                <el-icon><School /></el-icon> 我是教师
              </div>
            </div>

            <div class="input-grid">
              <el-form-item prop="name">
                <el-input 
                  v-model="form.name" 
                  placeholder="姓名" 
                  prefix-icon="UserFilled"
                  class="custom-input"
                />
              </el-form-item>

              <el-form-item prop="username">
                <el-input 
                  v-model="form.username" 
                  placeholder="用户名" 
                  prefix-icon="User"
                  class="custom-input"
                />
              </el-form-item>
            </div>

            <el-form-item prop="password">
              <el-input 
                v-model="form.password" 
                type="password" 
                placeholder="设置密码" 
                show-password 
                prefix-icon="Lock"
                class="custom-input"
              />
            </el-form-item>

            <transition name="fade-slide">
              <div v-if="form.role === 'student'" class="student-fields input-grid">
                <el-form-item prop="student_number">
                  <el-input 
                    v-model="form.student_number" 
                    placeholder="学号 (选填)" 
                    prefix-icon="CreditCard"
                    class="custom-input"
                  />
                </el-form-item>
                <el-form-item prop="class_id">
                  <el-input 
                    v-model.number="form.class_id" 
                    placeholder="班级ID (选填)" 
                    prefix-icon="Collection"
                    class="custom-input"
                  />
                </el-form-item>
              </div>
            </transition>

            <div class="form-actions">
              <el-button type="primary" class="submit-btn" :loading="loading" @click="handleRegister">
                立即注册
              </el-button>
            </div>
            
            <div class="form-footer">
              <span>已有账号？</span>
              <router-link to="/login" class="link-text">直接登录</router-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  role: 'student',
  name: '',
  username: '',
  password: '',
  student_number: '',
  class_id: null as number | null
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.register(form)
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (e: any) {
        ElMessage.error(e.response?.data?.detail || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.auth-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #eef2f6 100%);
  overflow: hidden;
}

.background-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 0;
  
  .shape {
    position: absolute;
    filter: blur(90px);
    opacity: 0.5;
    animation: float 15s infinite ease-in-out;
  }
  
  .shape-1 {
    top: -15%;
    left: -5%;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, #3b82f6 0%, rgba(59, 130, 246, 0) 70%);
  }
  
  .shape-2 {
    bottom: -10%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, #8b5cf6 0%, rgba(139, 92, 246, 0) 70%);
    animation-delay: -5s;
  }
}

.glass-panel {
  position: relative;
  z-index: 1;
  width: 1100px;
  height: 650px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 32px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.08);
  display: flex;
  overflow: hidden;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.12);
  }
}

.left-panel {
  flex: 0 0 40%;
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  position: relative;
  padding: 60px 48px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  
  .panel-bg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDQwIDQwIj48ZyBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0wIDQwaDQwVjBIMHY0MHptMjAtMjBoMjB2MjBIMjBWMjB6TTAgMjBoMjB2MjBIMFYyMHoiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvZz48L3N2Zz4=');
    opacity: 0.3;
  }
  
  .brand-content {
    position: relative;
    z-index: 2;
  }

  .logo-area {
    margin-bottom: 48px;
    .brand-title {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin: 0;
    }
  }
  
  .welcome-title {
    font-size: 40px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 24px;
  }
  
  .brand-desc {
    font-size: 16px;
    line-height: 1.6;
    opacity: 0.9;
    margin-bottom: 48px;
  }
  
  .quote-box {
    background: rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(10px);
    border-left: 4px solid #a5b4fc;
    
    .quote-text {
      font-size: 15px;
      font-style: italic;
      line-height: 1.6;
      margin-bottom: 12px;
      opacity: 0.95;
    }
    
    .quote-author {
      font-size: 13px;
      text-align: right;
      opacity: 0.8;
      font-weight: 600;
    }
  }
}

.right-panel {
  flex: 1;
  padding: 48px 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  
  .form-container {
    width: 100%;
    max-width: 480px;
  }
  
  .form-header {
    margin-bottom: 32px;
    text-align: center;
    
    h3 {
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 8px;
    }
    
    .subtitle {
      color: #6b7280;
      font-size: 15px;
    }
  }
}

.role-selector-mini {
  display: flex;
  background: #f3f4f6;
  padding: 4px;
  border-radius: 12px;
  margin-bottom: 32px;
  
  .role-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
    
    &.active {
      background: #fff;
      color: #4f46e5;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    &:hover:not(.active) {
      color: #4b5563;
    }
  }
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  
  .el-form-item {
    margin-bottom: 24px;
  }
}

.custom-input {
  :deep(.el-input__wrapper) {
    background: #f9fafb;
    box-shadow: none;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px 16px;
    transition: all 0.3s;
    
    &:hover, &.is-focus {
      background: #fff;
      border-color: #4f46e5;
      box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
  }
  
  :deep(.el-input__inner) {
    height: 44px;
    font-size: 15px;
  }
}

.submit-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(90deg, #4f46e5 0%, #4338ca 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3);
  }
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #6b7280;
  
  .link-text {
    color: #4f46e5;
    text-decoration: none;
    font-weight: 600;
    margin-left: 6px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
