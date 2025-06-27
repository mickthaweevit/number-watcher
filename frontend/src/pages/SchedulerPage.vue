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
    
    <!-- Backup Section -->
    <div class="border-t pt-4 mt-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">Database Backup</h3>
      <div class="flex flex-wrap gap-3 mb-4">
        <button
          @click="exportData"
          :disabled="loading"
          class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Export Backup
        </button>
        
        <label class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 cursor-pointer disabled:bg-gray-400">
          <input
            type="file"
            accept=".json"
            @change="handleFileImport"
            class="hidden"
            :disabled="loading"
          />
          Import Backup
        </label>
      </div>
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
            :disabled="loading || importLoading || !startDate || !endDate"
            class="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <svg v-if="importLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ importLoading ? 'Importing...' : 'Import Range' }}
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
    
    <!-- Import Logs Section -->
    <div class="border-t pt-4 mt-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-lg font-semibold text-gray-800">Import Logs</h3>
        <div class="flex items-center gap-3">
          <p class="text-sm text-gray-600">Showing latest 20 imports</p>
          <button
            @click="clearImportLogs"
            :disabled="loading || importLogs.length === 0"
            class="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Clear Logs
          </button>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Records</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Games</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Results</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-if="importLogs.length === 0">
              <td colspan="7" class="px-3 py-4 text-center text-gray-500">No import logs found</td>
            </tr>
            <tr v-for="log in importLogs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm text-gray-900">{{ log.filename || '-' }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ log.import_type }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ formatDateTime(log.started_at) }}</td>
              <td class="px-3 py-2 text-sm">
                <span class="px-2 py-1 rounded text-xs font-medium" :class="getStatusClass(log.status)">
                  {{ log.status }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ log.records_processed }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ log.games_created }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ log.results_created }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Messages -->
    <div v-if="message" class="mt-4 p-3 rounded" :class="messageClass">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { gameApi, type SchedulerStatus, type DateRangeImportResult } from '../services/api';
import type { ImportLog } from '../types';

const status = ref<SchedulerStatus | null>(null);
const loading = ref(false);
const importLoading = ref(false);
const message = ref('');
const messageClass = ref('');
const startDate = ref('');
const endDate = ref('');
const importLogs = ref<ImportLog[]>([]);
let logsIntervalId: number | null = null;



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

const fetchImportLogs = async () => {
  try {
    importLogs.value = await gameApi.getImportLogs();
  } catch (error) {
    console.error('Failed to fetch import logs:', error);
  }
};

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString();
};

const getStatusClass = (status: string) => {
  switch (status) {
    case 'success':
      return 'bg-green-100 text-green-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'running':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const clearImportLogs = async () => {
  if (!confirm('Are you sure you want to clear all import logs?')) {
    return;
  }
  
  try {
    loading.value = true;
    const result = await gameApi.clearImportLogs();
    showMessage(`${result.logs_deleted} import logs cleared successfully`);
    await fetchImportLogs();
  } catch (error) {
    console.error('Failed to clear import logs:', error);
    showMessage('Failed to clear import logs', 'error');
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

const exportData = async () => {
  try {
    loading.value = true;
    const backupData = await gameApi.exportData();
    
    // Create and download file
    const blob = new Blob([JSON.stringify(backupData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `numwatch-backup-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showMessage(`Backup exported: ${backupData.stats.total_games} games, ${backupData.stats.total_results} results`);
    
  } catch (error) {
    console.error('Failed to export data:', error);
    showMessage('Failed to export backup', 'error');
  } finally {
    loading.value = false;
  }
};

const handleFileImport = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (!file) return;
  
  try {
    loading.value = true;
    const text = await file.text();
    const backupData = JSON.parse(text);
    
    // Add filename and file size to backup data
    backupData._metadata = {
      filename: file.name,
      file_size: file.size
    };
    
    const result = await gameApi.importBackup(backupData);
    
    showMessage(
      `Backup imported successfully: ${result.games_created} games created, ${result.results_created} results created`
    );
    
    // Refresh status and logs after import
    await refreshStatus();
    await fetchImportLogs();
    
  } catch (error) {
    console.error('Failed to import backup:', error);
    showMessage('Failed to import backup', 'error');
    await fetchImportLogs(); // Refresh logs to show failed import
  } finally {
    loading.value = false;
    // Reset file input
    target.value = '';
  }
};

const importDateRange = async () => {
  if (!startDate.value || !endDate.value) {
    showMessage('Please select both start and end dates', 'error');
    return;
  }
  
  try {
    importLoading.value = true;
    showMessage('Starting date range import...', 'success');
    
    // Convert dates to ISO format
    const startISO = new Date(startDate.value).toISOString();
    const endISO = new Date(endDate.value).toISOString();
    
    const result: DateRangeImportResult = await gameApi.importDateRange(startISO, endISO);
    
    showMessage(
      `Date range import completed: ${result.successful_dates}/${result.total_dates} dates successful. ` +
      `Games created: ${result.total_games_created}, Results updated: ${result.total_results_updated}`
    );
    
    // Refresh status and logs after import
    await refreshStatus();
    await fetchImportLogs();
    
  } catch (error) {
    console.error('Failed to import date range:', error);
    showMessage('Failed to import date range', 'error');
    await fetchImportLogs(); // Refresh logs to show any failed imports
  } finally {
    importLoading.value = false;
  }
};

onMounted(() => {
  refreshStatus();
  fetchImportLogs();
  
  // Set default dates (last 7 days)
  const today = new Date();
  const lastWeek = new Date(today);
  lastWeek.setDate(today.getDate() - 7);
  
  endDate.value = today.toISOString().split('T')[0];
  startDate.value = lastWeek.toISOString().split('T')[0];
  
  // Auto-refresh logs every 10 seconds
  logsIntervalId = setInterval(fetchImportLogs, 10000);
});

onUnmounted(() => {
  // Clear logs interval when component unmounts
  if (logsIntervalId) {
    clearInterval(logsIntervalId);
  }
});
</script>