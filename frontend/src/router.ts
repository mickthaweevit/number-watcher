import { createRouter, createWebHistory } from 'vue-router'
import ResultsPage from './pages/ResultsPage.vue'
import SchedulerPage from './pages/SchedulerPage.vue'
import DashboardPage from './pages/DashboardPage.vue'

const routes = [
  {
    path: '/',
    name: 'Results',
    component: ResultsPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage
  },
  {
    path: '/scheduler',
    name: 'Scheduler',
    component: SchedulerPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router