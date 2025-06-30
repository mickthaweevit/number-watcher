<template>
  <div class="font-sans">
    <!-- Show header only when not on login page -->
    <header v-if="$route.name !== 'Login'" class="p-5 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">NumWatch - Number Result Tracker</h1>
          <div class="mt-1">
            <SchedulerStatus />
          </div>
        </div>
        
        <!-- Navigation -->
        <nav class="flex gap-4 items-center">
          <!-- API Source Selector -->
          <select 
            v-model="selectedApiSource" 
            @change="updateApiSource"
            class="text-sm border border-gray-300 rounded px-2 py-1 bg-white mr-2"
          >
            <option value="old">Source 1 (Old)</option>
            <option value="new">Source 2 (New)</option>
          </select>
          <router-link 
            to="/" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/results" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/results' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Results
          </router-link>
          <router-link 
            to="/scheduler" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/scheduler' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Scheduler
          </router-link>
          <router-link 
            v-if="isAdmin"
            to="/admin" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/admin' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Admin
          </router-link>
          <button 
            @click="logout"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </nav>
      </div>
    </header>
    
    <main :class="$route.name === 'Login' ? '' : 'p-6'">
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