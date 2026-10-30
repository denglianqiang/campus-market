<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 依赖route变化:登录/退出跳转后重新读取localStorage,导航栏状态才会刷新
const username = computed(() => {
  route.fullPath
  return localStorage.getItem('username') || ''
})

// 退出登录:清除localStorage里的登录态,回到登录页
function logout() {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<template>
  <header class="navbar">
    <div class="nav-inner">
      <router-link to="/" class="brand">🌱 校园二手闲置市场</router-link>
      <nav class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/publish">发布闲置</router-link>
        <router-link to="/my">我的管理</router-link>
      </nav>
      <div class="nav-user">
        <template v-if="username">
          <span class="hello">你好,{{ username }}</span>
          <button class="btn-sm btn-outline" @click="logout">退出登录</button>
        </template>
        <router-link v-else to="/login">
          <button class="btn-sm btn-primary">登录 / 注册</button>
        </router-link>
      </div>
    </div>
  </header>
  <router-view />
</template>

<style scoped>
.navbar {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}
.nav-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 16px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 28px;
}
.brand {
  font-size: 18px;
  font-weight: bold;
  color: #10b981;
}
.nav-links {
  display: flex;
  gap: 20px;
  flex: 1;
}
.nav-links a {
  color: #555;
  font-size: 15px;
  padding: 6px 2px;
}
.nav-links a.router-link-active {
  color: #10b981;
  font-weight: bold;
  border-bottom: 2px solid #10b981;
}
.nav-user {
  display: flex;
  align-items: center;
  gap: 10px;
}
.hello {
  font-size: 14px;
  color: #666;
}
</style>
