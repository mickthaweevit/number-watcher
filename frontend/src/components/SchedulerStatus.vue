<template>
  <div class="flex items-center gap-4 text-sm">
    <!-- API Status -->
    <div class="flex items-center gap-1">
      <span class="text-gray-600">API:</span>
      <span :class="apiStatus.includes('เชื่อมต่อแล้ว') ? 'text-green-600' : 'text-red-600'">
        {{ apiStatus }}
      </span>
    </div>
    
    <!-- Scheduler Status -->
    <div v-if="status" class="flex items-center gap-4">
      <div class="flex items-center gap-1">
        <span class="text-gray-600">Scheduler:</span>
        <span :class="status.is_running ? 'text-green-600' : 'text-red-600'">
          {{ status.is_running ? 'ทำงาน' : 'หยุด' }}
        </span>
      </div>
      
      <div class="flex items-center gap-1">
        <span class="text-gray-600">งาน:</span>
        <span class="text-blue-600">{{ status.next_jobs?.length || 0 }}</span>
      </div>
      
      <div v-if="!status.external_api_configured" class="flex items-center gap-1">
        <span class="text-orange-600">⚠ ยังไม่ได้ตั้งค่า API</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { gameApi, type SchedulerStatus } from '../services/api'

const apiStatus = ref('กำลังตรวจสอบ...')
const status = ref<SchedulerStatus | null>(null)

// Request cancellation
let abortController: AbortController | null = null
let intervalId: number | null = null

const checkStatus = async () => {
  try {
    // Cancel previous request if exists
    if (abortController) {
      abortController.abort()
    }
    
    // Create new abort controller
    abortController = new AbortController()
    
    // Check API health
    const healthResponse = await gameApi.healthCheck()
    apiStatus.value = `เชื่อมต่อแล้ว ${healthResponse.status}`
    
    // Check scheduler status
    status.value = await gameApi.getSchedulerStatus(abortController.signal)
  } catch (error: any) {
    // Don't show error if request was cancelled
    if (error.name !== 'AbortError') {
      apiStatus.value = 'การเชื่อมต่อล้มเหลว'
      console.error('Status check failed:', error)
    }
  }
}

onMounted(() => {
  checkStatus()
  
  // Refresh status every 30 seconds
  intervalId = setInterval(checkStatus, 30000)
})

onUnmounted(() => {
  // Cancel any pending requests
  if (abortController) {
    abortController.abort()
  }
  
  // Clear interval
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>