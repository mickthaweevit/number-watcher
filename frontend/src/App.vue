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
import { useRouter } from 'vue-router'
import SchedulerStatus from './components/SchedulerStatus.vue'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('auth_token')
  router.push('/login')
}
</script>