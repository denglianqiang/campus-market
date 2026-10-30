<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import API from '../api'

const router = useRouter()
const keyword = ref('')
const category = ref('')
const page = ref(1)
const pages = ref(0)
const total = ref(0)
const items = ref([])
const loading = ref(false)

// 分类标签(加分项2),与后端示例数据的分类保持一致
const categories = ['教材书籍', '电子产品', '生活用品', '运动用品']

let timer = null
// 搜索防抖:停止输入300ms后才发请求,避免每敲一个字就请求一次(必做:搜索)
function onSearchInput() {
  clearTimeout(timer)
  timer = setTimeout(() => {
    page.value = 1
    fetchItems()
  }, 300)
}

function pickCategory(c) {
  // 再点一次同一个分类=取消筛选
  category.value = category.value === c ? '' : c
  page.value = 1
  fetchItems()
}

// 根据当前关键词/分类/页码向后端拉取一页物品列表
async function fetchItems() {
  loading.value = true
  try {
    const { data } = await API.get('/items', {
      params: { keyword: keyword.value, category: category.value, page: page.value }
    })
    items.value = data.items
    total.value = data.total
    pages.value = data.pages
  } finally {
    loading.value = false
  }
}

// 翻页:不能越过第1页(上一页)或最后一页(下一页),越界时按钮本身已被禁用,这里是双保险
function prev() {
  if (page.value > 1) {
    page.value--
    fetchItems()
  }
}

function next() {
  if (page.value < pages.value) {
    page.value++
    fetchItems()
  }
}

// 没有图片时按分类显示一个占位图标
function emoji(c) {
  return { 教材书籍: '📚', 电子产品: '💻', 生活用品: '🏠', 运动用品: '🏀' }[c] || '📦'
}

onMounted(fetchItems)
</script>

<template>
  <div class="page">
    <!-- 搜索框(必做):输入即过滤 -->
    <div class="search-bar card">
      <input v-model="keyword" @input="onSearchInput" placeholder="🔍 搜索闲置物品标题..." />
    </div>

    <!-- 分类筛选(加分项2) -->
    <div class="cat-bar">
      <span :class="{ active: category === '' }" @click="pickCategory('')">全部</span>
      <span
        v-for="c in categories"
        :key="c"
        :class="{ active: category === c }"
        @click="pickCategory(c)"
      >
        {{ c }}
      </span>
    </div>

    <!-- 物品列表(必做):标题/摘要/价格/发布时间 -->
    <div v-if="loading" class="empty">加载中...</div>
    <div v-else-if="items.length === 0" class="empty">没有找到相关物品 🤔</div>
    <div v-else class="grid">
      <div v-for="it in items" :key="it.id" class="card item" @click="router.push(`/items/${it.id}`)">
        <img v-if="it.image_url" :src="it.image_url" class="pic" />
        <div v-else class="pic placeholder">{{ emoji(it.category) }}</div>
        <div class="info">
          <div class="title-row">
            <h3>{{ it.title }}</h3>
            <span :class="['badge', it.status === '已售' ? 'sold' : 'on']">{{ it.status }}</span>
          </div>
          <p class="desc">{{ it.description || '暂无描述' }}</p>
          <div class="bottom">
            <span class="price">¥{{ it.price }}</span>
            <span class="meta">{{ it.category }} · {{ it.created_at }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页(加分项3):每页5条 -->
    <div v-if="pages > 1" class="pager">
      <button class="btn-outline btn-sm" :disabled="page <= 1" @click="prev">上一页</button>
      <span>第 {{ page }} / {{ pages }} 页(共{{ total }}条)</span>
      <button class="btn-outline btn-sm" :disabled="page >= pages" @click="next">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  margin-bottom: 14px;
}
.search-bar input {
  border: none;
  font-size: 15px;
  padding-left: 0;
}
.cat-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.cat-bar span {
  padding: 6px 16px;
  background: #fff;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  border: 1px solid #e5e7eb;
}
.cat-bar span.active {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.item {
  display: flex;
  gap: 14px;
  cursor: pointer;
  transition: transform 0.15s;
}
.item:hover {
  transform: translateY(-2px);
}
.pic {
  width: 110px;
  height: 110px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  background: #f0fdf4;
}
.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.title-row h3 {
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.badge {
  flex-shrink: 0;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}
.badge.on {
  background: #d1fae5;
  color: #059669;
}
.badge.sold {
  background: #e5e7eb;
  color: #6b7280;
}
.desc {
  font-size: 13px;
  color: #888;
  margin: 6px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.bottom {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.price {
  color: #ef4444;
  font-weight: bold;
  font-size: 17px;
}
.meta {
  font-size: 12px;
  color: #aaa;
}
.pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
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
  padding: 60px 0;
}
</style>
