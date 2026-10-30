<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import API from '../api'

const route = useRoute()
const router = useRouter()
const item = ref(null)
const isOwner = ref(false)
// 登录时后端返回并存入localStorage的用户ID(0表示未登录)
const myId = Number(localStorage.getItem('user_id'))

// 根据路由里的id拉取物品详情,判断当前用户是否为发布者
async function fetchItem() {
  const { data } = await API.get(`/items/${route.params.id}`)
  item.value = data
  // 判断当前登录用户是否是发布者,是则展示编辑/删除/状态按钮
  isOwner.value = myId === data.user_id
}

// 切换在售/已售状态(加分项4)
async function toggleStatus() {
  const next = item.value.status === '在售' ? '已售' : '在售'
  await API.put(`/items/${item.value.id}`, { status: next, user_id: myId })
  item.value.status = next
}

// 删除自己的物品(必做:我的管理)
async function remove() {
  if (!confirm(`确定删除「${item.value.title}」吗?`)) return
  await API.delete(`/items/${item.value.id}`, { params: { user_id: myId } })
  alert('删除成功')
  router.push('/')
}

onMounted(fetchItem)
</script>

<template>
  <div class="page" v-if="item">
    <button class="btn-outline btn-sm back" @click="router.back()">← 返回列表</button>

    <div class="card detail">
      <img v-if="item.image_url" :src="item.image_url" class="pic" />
      <div v-else class="pic placeholder">📦</div>

      <div class="body">
        <div class="title-row">
          <h2>{{ item.title }}</h2>
          <span :class="['badge', item.status === '已售' ? 'sold' : 'on']">{{ item.status }}</span>
        </div>
        <p class="price">¥{{ item.price }}</p>
        <p class="meta">分类:{{ item.category || '未分类' }}</p>
        <p class="meta">发布时间:{{ item.created_at }}</p>
        <div class="desc">
          <h4>物品描述</h4>
          <p>{{ item.description || '暂无描述' }}</p>
        </div>

        <!-- 发布者才可见的操作区 -->
        <div v-if="isOwner" class="owner-actions">
          <button class="btn-outline" @click="router.push(`/edit/${item.id}`)">✏️ 编辑</button>
          <button class="btn-outline" @click="toggleStatus">
            {{ item.status === '在售' ? '标记为已售' : '重新上架' }}
          </button>
          <button class="btn-danger" @click="remove">🗑 删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back {
  margin-bottom: 14px;
}
.detail {
  display: flex;
  gap: 24px;
}
.pic {
  width: 280px;
  height: 280px;
  border-radius: 10px;
  object-fit: cover;
  flex-shrink: 0;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px;
  background: #f0fdf4;
}
.body {
  flex: 1;
}
.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.badge {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
}
.badge.on {
  background: #d1fae5;
  color: #059669;
}
.badge.sold {
  background: #e5e7eb;
  color: #6b7280;
}
.price {
  color: #ef4444;
  font-size: 26px;
  font-weight: bold;
  margin: 12px 0;
}
.meta {
  font-size: 13px;
  color: #888;
  margin-bottom: 6px;
}
.desc {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed #e5e7eb;
}
.desc h4 {
  font-size: 14px;
  margin-bottom: 8px;
}
.desc p {
  font-size: 14px;
  color: #555;
  line-height: 1.7;
  white-space: pre-wrap;
}
.owner-actions {
  margin-top: 22px;
  display: flex;
  gap: 10px;
}
</style>
