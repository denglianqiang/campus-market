<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import API from '../api'

const route = useRoute()
const router = useRouter()
// 路由带id参数=编辑模式(复用本组件),否则=发布模式
const isEdit = !!route.params.id
const form = ref({ title: '', description: '', price: null, category: '', image_url: '' })
const aiLoading = ref(false)
const aiSource = ref('') // 记录描述来源:ai=大模型生成 / template=本地模板
const myId = Number(localStorage.getItem('user_id'))

const categories = ['教材书籍', '电子产品', '生活用品', '运动用品']

onMounted(async () => {
  if (!isEdit) return
  // 编辑模式:先拉取原数据回填表单
  const { data } = await API.get(`/items/${route.params.id}`)
  if (data.user_id !== myId) {
    alert('只能编辑自己发布的物品')
    router.push('/')
    return
  }
  form.value = {
    title: data.title,
    description: data.description,
    price: data.price,
    category: data.category,
    image_url: data.image_url
  }
})

// 提交表单:编辑模式走PUT更新,发布模式走POST新建,成功后都跳到"我的管理"
async function submit() {
  if (!form.value.title.trim()) {
    alert('标题不能为空')
    return
  }
  if (isEdit) {
    await API.put(`/items/${route.params.id}`, { ...form.value, user_id: myId })
    alert('修改成功')
  } else {
    await API.post('/items', { ...form.value, user_id: myId })
    alert('发布成功')
  }
  router.push('/my')
}

// AI生成描述(加分项5):后端配置了AI_API_KEY时走大模型,否则走本地模板
async function genDescription() {
  if (!form.value.title.trim()) {
    alert('请先填写物品名称')
    return
  }
  aiLoading.value = true
  try {
    const { data } = await API.post('/ai/description', {
      title: form.value.title,
      category: form.value.category
    })
    form.value.description = data.description
    aiSource.value = data.source
  } finally {
    aiLoading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="card form-card">
      <h2>{{ isEdit ? '✏️ 编辑闲置' : '📝 发布闲置' }}</h2>

      <div class="field">
        <label>物品名称 *</label>
        <input v-model="form.title" placeholder="例如:iPad Air 5 64G 蓝色" />
      </div>

      <div class="row">
        <div class="field">
          <label>价格(元)</label>
          <input v-model="form.price" type="number" min="0" step="0.01" placeholder="0.00" />
        </div>
        <div class="field">
          <label>分类</label>
          <select v-model="form.category">
            <option value="">未分类</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>图片URL(选填)</label>
        <input v-model="form.image_url" placeholder="https://..." />
      </div>

      <div class="field">
        <label>
          物品描述
          <button class="btn-outline btn-sm ai-btn" :disabled="aiLoading" @click="genDescription">
            {{ aiLoading ? 'AI生成中...' : '✨ AI生成描述' }}
          </button>
          <span v-if="aiSource" class="ai-tag">
            {{ aiSource === 'ai' ? '大模型生成' : '模板生成(未配置AI Key)' }}
          </span>
        </label>
        <textarea v-model="form.description" rows="5" placeholder="描述成色、购买渠道、转让原因等..."></textarea>
      </div>

      <button class="btn-primary submit" @click="submit">
        {{ isEdit ? '保存修改' : '立即发布' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.form-card {
  max-width: 640px;
  margin: 0 auto;
}
h2 {
  margin-bottom: 20px;
  font-size: 18px;
}
.field {
  margin-bottom: 16px;
}
.field label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}
.row {
  display: flex;
  gap: 16px;
}
.row .field {
  flex: 1;
}
.ai-btn {
  margin-left: auto;
}
.ai-tag {
  font-size: 11px;
  color: #999;
}
textarea {
  resize: vertical;
}
.submit {
  width: 100%;
  padding: 12px;
  font-size: 15px;
}
</style>
