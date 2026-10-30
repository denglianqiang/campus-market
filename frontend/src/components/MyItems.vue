<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import API from '../api'

const router = useRouter()
const items = ref([])
const page = ref(1)
const pages = ref(0)
const total = ref(0)
// 登录时后端返回并存入localStorage的用户ID
const myId = Number(localStorage.getItem('user_id'))

async function fetchMine() {
  const { data } = await API.get('/my/items', {
    params: { user_id: myId, page: page.value }
  })
  items.value = data.items
  total.value = data.total
  pages.value = data.pages
}

// 一键切换在售/已售状态(加分项4)
async function toggleStatus(item) {
  const next = item.status === '在售' ? '已售' : '在售'
  await API.put(`/items/${item.id}`, { status: next, user_id: myId })
  item.status = next
}

// 删除(必做:我的管理)
async function remove(item) {
  if (!confirm(`确定删除「${item.title}」吗?`)) return
  await API.delete(`/items/${item.id}`, { params: { user_id: myId } })
  fetchMine()
}

// 翻页:越界判断与按钮disabled双重保险
function prev() {
  if (page.value > 1) {
    page.value--
    fetchMine()
  }
}

function next() {
  if (page.value < pages.value) {
    page.value++
    fetchMine()
  }
}

onMounted(fetchMine)
</script>

<template>
  <div class="page">
    <div class="card">
      <h2>📦 我发布的闲置({{ total }})</h2>

      <div v-if="items.length === 0" class="empty">
        还没有发布过物品,<router-link to="/publish" class="link">去发布</router-link>
      </div>

      <div v-else class="list">
        <div v-for="it in items" :key="it.id" class="row-item">
          <div class="main" @click="router.push(`/items/${it.id}`)">
            <h4>{{ it.title }}</h4>
            <p class="meta">{{ it.category }} · {{ it.created_at }}</p>
          </div>
          <span class="price">¥{{ it.price }}</span>
          <span :class="['badge', it.status === '已售' ? 'sold' : 'on']">{{ it.status }}</span>
          <div class="ops">
            <button class="btn-outline btn-sm" @click="toggleStatus(it)">
              {{ it.status === '在售' ? '标记已售' : '重新上架' }}
            </button>
            <button class="btn-outline btn-sm" @click="router.push(`/edit/${it.id}`)">编辑</button>
            <button class="btn-danger btn-sm" @click="remove(it)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="pages > 1" class="pager">
        <button class="btn-outline btn-sm" :disabled="page <= 1" @click="prev">上一页</button>
        <span>第 {{ page }} / {{ pages }} 页</span>
        <button class="btn-outline btn-sm" :disabled="page >= pages" @click="next">下一页</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
h2 {
  font-size: 17px;
  margin-bottom: 16px;
}
.list {
  display: flex;
  flex-direction: column;
}
.row-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid #f0f0f0;
}
.row-item:last-child {
  border-bottom: none;
}
.main {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}
.main h4 {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
}
.price {
  color: #ef4444;
  font-weight: bold;
}
.badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}
.badge.on {
  background: #d1fae5;
  color: #059669;
}
.badge.sold {
  background: #e5e7eb;
  color: #6b7280;
}
.ops {
  display: flex;
  gap: 8px;
}
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  font-size: 14px;
  color: #666;
}
.pager button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.empty {
  text-align: center;
  color: #999;
  padding: 40px 0;
}
.link {
  color: #10b981;
}
</style>
