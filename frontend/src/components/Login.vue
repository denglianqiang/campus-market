<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import API from '../api'

const router = useRouter()
const mode = ref('login') // login=登录Tab, register=注册Tab(加分项1)
const username = ref('')
const password = ref('')
const confirmPwd = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  if (mode.value === 'register' && password.value !== confirmPwd.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  try {
    if (mode.value === 'login') {
      // 登录成功:后端返回用户ID,存入localStorage保持登录态(任务书要求的简易方案)
      const { data } = await API.post('/login', {
        username: username.value,
        password: password.value
      })
      localStorage.setItem('user_id', data.id)
      localStorage.setItem('username', data.username)
      router.push('/')
    } else {
      await API.post('/register', {
        username: username.value,
        password: password.value
      })
      alert('注册成功,请登录')
      mode.value = 'login'
    }
  } catch (e) {
    // 后端返回的错误已由api.js拦截器统一alert,这里无需重复处理
  }
}
</script>

<template>
  <div class="page login-page">
    <div class="card login-card">
      <div class="tabs">
        <span :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</span>
        <span :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</span>
      </div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" placeholder="测试账号:user1 / user2" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="测试密码:123456" />
        </div>
        <div v-if="mode === 'register'" class="field">
          <label>确认密码</label>
          <input v-model="confirmPwd" type="password" placeholder="再次输入密码" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-primary submit">
          {{ mode === 'login' ? '登 录' : '注 册' }}
        </button>
      </form>

      <p class="tip">预置测试账号:user1 / 123456,user2 / 123456</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
}
.login-card {
  width: 380px;
  margin-top: 60px;
}
.tabs {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}
.tabs span {
  padding: 10px 4px;
  cursor: pointer;
  color: #888;
  font-size: 15px;
}
.tabs span.active {
  color: #10b981;
  font-weight: bold;
  border-bottom: 2px solid #10b981;
}
.field {
  margin-bottom: 16px;
}
.field label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}
.error {
  color: #ef4444;
  font-size: 13px;
  margin-bottom: 12px;
}
.submit {
  width: 100%;
  padding: 11px;
  font-size: 15px;
}
.tip {
  margin-top: 16px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
</style>
