import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from './pages/LoginPage.vue'
import ResultsPage from './pages/ResultsPage.vue'
import SchedulerPage from './pages/SchedulerPage.vue'
import DashboardPage from './pages/DashboardPage.vue'

// Auth guard function
const requireAuth = (to: any, from: any, next: any) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    next()
  } else {
    next('/login')
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardPage,
    beforeEnter: requireAuth
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsPage,
    beforeEnter: requireAuth
  },
  {
    path: '/scheduler',
    name: 'Scheduler',
    component: SchedulerPage,
    beforeEnter: requireAuth
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('./pages/AdminPage.vue'),
    beforeEnter: requireAuth
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router