<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Scheduler Control</h2>
    
    <!-- Status Display -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-gray-50 p-3 rounded">
        <div class="text-sm text-gray-600">Status</div>
        <div class="font-semibold" :class="status?.is_running ? 'text-green-600' : 'text-red-600'">
          {{ status?.is_running ? 'Running' : 'Stopped' }}
        </div>
      </div>
      
      <div class="bg-gray-50 p-3 rounded">
        <div class="text-sm text-gray-600">API Configured</div>
        <div class="font-semibold" :class="status?.external_api_configured ? 'text-green-600' : 'text-orange-600'">
          {{ status?.external_api_configured ? 'Yes' : 'No' }}
        </div>
      </div>
      
      <div class="bg-gray-50 p-3 rounded">
        <div class="text-sm text-gray-600">Thread Status</div>
        <div class="font-semibold" :class="status?.thread_alive ? 'text-green-600' : 'text-gray-600'">
          {{ status?.thread_alive ? 'Active' : 'Inactive' }}
        </div>
      </div>
      
      <div class="bg-gray-50 p-3 rounded">
        <div class="text-sm text-gray-600">Scheduled Jobs</div>
        <div class="font-semibold text-blue-600">
          {{ status?.next_jobs?.length || 0 }}
        </div>
      </div>
    </div>
    
    <!-- Control Buttons -->
    <div class="flex flex-wrap gap-3 mb-4">
      <button
        @click="startScheduler"
        :disabled="loading || status?.is_running"
        class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Start Scheduler
      </button>
      
      <button
        @click="stopScheduler"
        :disabled="loading || !status?.is_running"
        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Stop Scheduler
      </button>
      
      <button
        @click="triggerImport"
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Manual Import
      </button>
      
      <button
        @click="refreshStatus"
        :disabled="loading"
        class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Refresh Status
      </button>
    </div>
    
    <!-- Date Range Import Section -->
    <div class="border-t pt-4 mt-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">Date Range Import</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
          <input
            v-model="startDate"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
          <input
            v-model="endDate"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <button
            @click="importDateRange"
            :disabled="loading || !startDate || !endDate"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Import Range
          </button>
        </div>
      </div>
      <p class="text-sm text-gray-600 mt-2">Maximum 30 days allowed per import</p>
    </div>
    
    <!-- Next Jobs Display -->
    <div v-if="status?.next_jobs && status.next_jobs.length > 0" class="mt-4">
      <h3 class="text-sm font-semibold text-gray-700 mb-2">Scheduled Jobs:</h3>
      <div class="bg-gray-50 p-3 rounded text-sm">
        <div v-for="(job, index) in status.next_jobs" :key="index" class="text-gray-600">
          {{ job }}
        </div>
      </div>
    </div>
    
    <!-- Messages -->
    <div v-if="message" class="mt-4 p-3 rounded" :class="messageClass">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { gameApi, type SchedulerStatus, type DateRangeImportResult } from '../services/api';

const status = ref<SchedulerStatus | null>(null);
const loading = ref(false);
const message = ref('');
const messageClass = ref('');
const startDate = ref('');
const endDate = ref('');

const showMessage = (msg: string, type: 'success' | 'error' = 'success') => {
  message.value = msg;
  messageClass.value = type === 'success' 
    ? 'bg-green-100 text-green-800 border border-green-200'
    : 'bg-red-100 text-red-800 border border-red-200';
  
  setTimeout(() => {
    message.value = '';
  }, 5000);
};

const refreshStatus = async () => {
  try {
    loading.value = true;
    status.value = await gameApi.getSchedulerStatus();
  } catch (error) {
    console.error('Failed to fetch scheduler status:', error);
    showMessage('Failed to fetch scheduler status', 'error');
  } finally {
    loading.value = false;
  }
};

const startScheduler = async () => {
  try {
    loading.value = true;
    const result = await gameApi.startScheduler();
    status.value = result.status;
    showMessage('Scheduler started successfully');
  } catch (error) {
    console.error('Failed to start scheduler:', error);
    showMessage('Failed to start scheduler', 'error');
  } finally {
    loading.value = false;
  }
};

const stopScheduler = async () => {
  try {
    loading.value = true;
    const result = await gameApi.stopScheduler();
    status.value = result.status;
    showMessage('Scheduler stopped successfully');
  } catch (error) {
    console.error('Failed to stop scheduler:', error);
    showMessage('Failed to stop scheduler', 'error');
  } finally {
    loading.value = false;
  }
};

const triggerImport = async () => {
  try {
    loading.value = true;
    const result = await gameApi.triggerManualImport();
    showMessage(`Manual import completed: ${result.message}`);
    // Refresh status after import
    await refreshStatus();
  } catch (error) {
    console.error('Failed to trigger manual import:', error);
    showMessage('Failed to trigger manual import', 'error');
  } finally {
    loading.value = false;
  }
};

const importDateRange = async () => {
  if (!startDate.value || !endDate.value) {
    showMessage('Please select both start and end dates', 'error');
    return;
  }
  
  try {
    loading.value = true;
    
    // Convert dates to ISO format
    const startISO = new Date(startDate.value).toISOString();
    const endISO = new Date(endDate.value).toISOString();
    
    const result: DateRangeImportResult = await gameApi.importDateRange(startISO, endISO);
    
    showMessage(
      `Date range import completed: ${result.successful_dates}/${result.total_dates} dates successful. ` +
      `Games created: ${result.total_games_created}, Results updated: ${result.total_results_updated}`
    );
    
    // Refresh status after import
    await refreshStatus();
    
  } catch (error) {
    console.error('Failed to import date range:', error);
    showMessage('Failed to import date range', 'error');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  refreshStatus();
  
  // Set default dates (last 7 days)
  const today = new Date();
  const lastWeek = new Date(today);
  lastWeek.setDate(today.getDate() - 7);
  
  endDate.value = today.toISOString().split('T')[0];
  startDate.value = lastWeek.toISOString().split('T')[0];
});
</script>