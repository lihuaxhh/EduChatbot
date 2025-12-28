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
            <div class="brand-badge">AI Powered</div>
          </div>
          <h2 class="welcome-title">Unlock the New Era<br>of Intelligent Education</h2>
          <p class="brand-desc">
            Powered by cutting-edge AI, we provide personalized learning paths, intelligent grading, and real-time Q&A.
          </p>
          <div class="feature-list">
            <div class="feature-item">
              <span class="dot"></span>
              <span>Unlock learning potential, reshape education</span>
            </div>
            <div class="feature-item">
              <span class="dot"></span>
              <span>Data-driven teaching, precise improvement</span>
            </div>
            <div class="feature-item">
              <span class="dot"></span>
              <span>Always-on AI companion to answer every question</span>
            </div>
          </div>
        </div>
        <div class="panel-bg-overlay"></div>
      </div>

      <!-- Right Panel: Form -->
      <div class="right-panel">
        <div class="form-container">
          <div class="form-header">
            <h3>Welcome Back</h3>
            <p class="subtitle">Please log in to continue</p>
          </div>
          
          <el-form ref="formRef" :model="form" :rules="rules" class="auth-form" size="large">
            <el-form-item prop="username">
              <el-input 
                v-model="form.username" 
                placeholder="Username" 
                prefix-icon="User"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="form.password" 
                type="password" 
                placeholder="Password" 
                show-password 
                prefix-icon="Lock"
                @keyup.enter="handleLogin"
                class="custom-input"
              />
            </el-form-item>
            
            <div class="form-options">
              <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
              <a href="#" class="forgot-link">Forgot password?</a>
            </div>

            <div class="form-actions">
              <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">
                Sign In
              </el-button>
            </div>
            
            <div class="form-footer">
              <span>Don’t have an account?</span>
              <router-link to="/register" class="link-text">Create one</router-link>
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
const rememberMe = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(form)
        ElMessage.success('Signed in successfully')
        if (authStore.role === 'teacher' || authStore.role === 'admin') {
           router.push('/problems') 
        } else if (authStore.role === 'student') {
           router.push('/student-assignments')
        } else {
           router.push('/classes')
        }
      } catch (e: any) {
        ElMessage.error(e.response?.data?.detail || 'Sign in failed')
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
  width: 1000px;
  height: 600px;
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
  flex: 0 0 45%;
  background: linear-gradient(135deg, #2563EB 0%, #1e40af 100%);
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
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 48px;
    
    .brand-title {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin: 0;
    }
    
    .brand-badge {
      padding: 4px 8px;
      background: rgba(255,255,255,0.2);
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
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
  
  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    
    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 15px;
      font-weight: 500;
      
      .dot {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        box-shadow: 0 0 8px #4ade80;
      }
    }
  }
}

.right-panel {
  flex: 1;
  padding: 60px 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .form-container {
    width: 100%;
    max-width: 400px;
  }
  
  .form-header {
    margin-bottom: 40px;
    
    h3 {
      font-size: 32px;
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 8px;
    }
    
    .subtitle {
      color: #6b7280;
      font-size: 16px;
    }
  }
}

.custom-input {
  :deep(.el-input__wrapper) {
    background: #f9fafb;
    box-shadow: none;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px 16px;
    transition: all 0.3s;
    
    &:hover, &.is-focus {
      background: #fff;
      border-color: #2563EB;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
  }
  
  :deep(.el-input__inner) {
    height: 48px;
    font-size: 16px;
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  
  .forgot-link {
    font-size: 14px;
    color: #2563EB;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.submit-btn {
  width: 100%;
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(90deg, #2563EB 0%, #1d4ed8 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
  }
}

.form-footer {
  margin-top: 32px;
  text-align: center;
  font-size: 15px;
  color: #6b7280;
  
  .link-text {
    color: #2563EB;
    text-decoration: none;
    font-weight: 600;
    margin-left: 6px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
