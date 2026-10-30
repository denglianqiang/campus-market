import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './components/Login.vue'
import ItemList from './components/ItemList.vue'
import ItemDetail from './components/ItemDetail.vue'
import ItemPublish from './components/ItemPublish.vue'
import MyItems from './components/MyItems.vue'
import './style.css'

// 路由表:/edit复用发布组件(标题栏显示"编辑"),/items/:id为详情页
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: ItemList },
    { path: '/login', component: Login },
    { path: '/items/:id', component: ItemDetail },
    { path: '/publish', component: ItemPublish },
    { path: '/edit/:id', component: ItemPublish },
    { path: '/my', component: MyItems }
  ]
})

// 路由守卫:发布/编辑/我的管理需要登录态,未登录统一跳到登录页
router.beforeEach((to) => {
  const needLogin = ['/publish', '/my'].includes(to.path) || to.path.startsWith('/edit')
  if (needLogin && !localStorage.getItem('user_id')) {
    alert('请先登录')
    return '/login'
  }
})

createApp(App).use(router).mount('#app')
