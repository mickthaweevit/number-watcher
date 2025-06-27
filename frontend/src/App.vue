<template>
  <div class="font-sans">
    <header class="p-5 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">NumWatch - Number Result Tracker</h1>
          <div class="mt-1">
            <SchedulerStatus />
          </div>
        </div>
        
        <!-- Navigation -->
        <nav class="flex gap-4">
          <router-link 
            to="/" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Results
          </router-link>
          <router-link 
            to="/dashboard" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/dashboard' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/scheduler" 
            class="px-4 py-2 rounded transition-colors"
            :class="$route.path === '/scheduler' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-200'"
          >
            Scheduler
          </router-link>
        </nav>
      </div>
    </header>
    
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import SchedulerStatus from './components/SchedulerStatus.vue'
</script>