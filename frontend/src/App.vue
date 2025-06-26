<template>
  <div class="font-sans">
    <header class="p-5 bg-gray-50 border-b border-gray-200">
      <h1 class="text-2xl font-bold text-gray-800">NumWatch - Number Result Tracker</h1>
      <p class="mt-1 text-sm text-gray-600">API Status: {{ apiStatus }}</p>
    </header>
    
    <main class="p-6">
      <SchedulerControl />
      <ResultsTable />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { gameApi } from './services/api'
import ResultsTable from './components/ResultsTable.vue'
import SchedulerControl from './components/SchedulerControl.vue'

const apiStatus = ref('Checking...')

onMounted(async () => {
  try {
    const response = await gameApi.healthCheck()
    apiStatus.value = `Connected: ${response.status}`
  } catch (error) {
    apiStatus.value = 'API connection failed'
  }
})
</script>