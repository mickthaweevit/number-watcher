<template>
  <div class="font-sans">
    <!-- Show header only when not on login page -->
    <header v-if="$route.name !== 'Login'" class="p-3 md:p-5 bg-gray-50 border-b border-gray-200">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div class="flex-1">
          <h1 class="text-lg md:text-2xl font-bold text-gray-800">เลขไหนดี</h1>
          <div class="mt-1 hidden md:block">
            <SchedulerStatus />
          </div>
        </div>
        
        <!-- Navigation -->
        <nav class="flex flex-wrap gap-2 md:gap-4 items-center">
          <!-- API Source Selector -->
          <select 
            v-model="selectedApiSource" 
            @change="updateApiSource"
            class="text-xs md:text-sm border border-gray-300 rounded px-2 py-1 bg-white"
          >
            <option value="old">นอกบ้าน(punsook)</option>
            <option value="new">ในบ้าน(chom998)</option>
          </select>
          <router-link 
            to="/" 
            class="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm rounded transition-colors"
            :class="$route.path === '/' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            รายงาน
          </router-link>
          <router-link 
            to="/results" 
            class="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm rounded transition-colors"
            :class="$route.path === '/results' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            รวมผลหวย
          </router-link>
          <router-link
            to="/scheduler" 
            class="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm rounded transition-colors"
            :class="$route.path === '/scheduler' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            ตั้งค่า
          </router-link>
          <router-link 
            v-if="isAdmin"
            to="/admin" 
            class="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm rounded transition-colors"
            :class="$route.path === '/admin' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            ผู้ดูแล
          </router-link>
          <button 
            @click="logout"
            class="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            ออกจากระบบ
          </button>
        </nav>
        
        <!-- Mobile Scheduler Status -->
        <div class="md:hidden">
          <SchedulerStatus />
        </div>
      </div>
    </header>
    
    <main :class="$route.name === 'Login' ? '' : 'p-3 md:p-6'">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from './services/api'
import SchedulerStatus from './components/SchedulerStatus.vue'

const router = useRouter()
const route = useRoute()
const isAdmin = ref(false)
const selectedApiSource = ref('old')

const checkAdminStatus = async () => {
  try {
    const user = await authApi.getCurrentUser()
    isAdmin.value = user.is_admin
  } catch (error) {
    isAdmin.value = false
  }
}

const logout = () => {
  localStorage.removeItem('auth_token')
  router.push('/login')
}

const updateAdminStatus = () => {
  if (localStorage.getItem('auth_token')) {
    checkAdminStatus()
  } else {
    isAdmin.value = false
  }
}

const updateApiSource = () => {
  localStorage.setItem('selectedApiSource', selectedApiSource.value)
  // Trigger refresh of current page data
  window.location.reload()
}

// Load saved API source on mount
const loadApiSource = () => {
  const saved = localStorage.getItem('selectedApiSource')
  if (saved) {
    selectedApiSource.value = saved
  }
}

onMounted(() => {
  updateAdminStatus()
  loadApiSource()
})

// Update admin status when route changes (after login)
watch(() => route.path, () => {
  updateAdminStatus()
})
</script>