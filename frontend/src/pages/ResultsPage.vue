<template>
  <div class="p-5">
    <h2 class="text-xl font-semibold mb-4">NumWatch Results Table</h2>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-gray-600">Loading...</div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="text-red-800 font-medium mb-2">Error: {{ error }}</div>
      <button 
        @click="fetchResults" 
        class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Retry
      </button>
    </div>
    
    <!-- Main Content -->
    <div v-else>
      <!-- Result Type Tabs -->
      <div class="mb-4">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-6">
            <button
              v-for="tab in resultTabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                'py-1 px-1 border-b-2 font-medium text-xs',
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>
      </div>
      


      <!-- Results Table -->
      <div class="table-container border border-gray-300 rounded">
        <table class="min-w-full text-xs">
          <thead class="bg-gray-100 sticky-header">
            <tr>
              <th class="sticky-col-1 px-2 py-1 text-left font-medium text-gray-600 border-r border-gray-300">
                Game
              </th>
              <th 
                v-for="date in uniqueDates" 
                :key="date"
                class="date-column px-2 py-1 text-center font-medium text-gray-600 border-r border-gray-300 last:border-r-0"
              >
                {{ formatDate(date) }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white">
            <tr v-for="game in filteredTableData" :key="game.gameId" class="border-b border-gray-200 hover:bg-gray-50">
              <td class="sticky-col-1 px-2 py-1 text-gray-900 border-r border-gray-200 truncate max-w-32">
                {{ game.gameName }}
              </td>
              <td 
                v-for="date in uniqueDates" 
                :key="date"
                class="date-column px-2 py-1 text-center border-r border-gray-200 last:border-r-0"
                :class="getResultCellClass(game.results[date]?.[activeTab])"
              >
                <span v-if="game.results[date]?.[activeTab] === 'รอผล'" class="inline-block">
                  <svg class="w-3 h-3" viewBox="0 0 24 24">
                    <path fill="currentColor" :d="mdiTimerSand" />
                  </svg>
                </span>
                <span v-else-if="game.results[date]?.[activeTab] === 'ยกเลิก'" class="inline-block">
                  <svg class="w-3 h-3" viewBox="0 0 24 24">
                    <path fill="currentColor" :d="mdiCancel" />
                  </svg>
                </span>
                <span v-else>
                  {{ game.results[date]?.[activeTab] || '-' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer Info -->
      <div class="mt-3 text-xs text-gray-500">
        {{ filteredTableData.length }} games • {{ results.length }} results
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { gameApi } from '../services/api'
import type { Result, TableData, DateResult } from '../types'
import { mdiCancel, mdiTimerSand } from '@mdi/js'

// Reactive state
const results = ref<Result[]>([])
const tableData = ref<TableData[]>([])
const loading = ref(true)
// Removed category and country filters
const activeTab = ref('result_3up') // Default to 3-Up
const error = ref('')

// Request cancellation
let abortController: AbortController | null = null

// Tab configuration
const resultTabs = [
  { key: 'result_2down', label: '2-Down' },
  { key: 'result_3up', label: '3-Up' },
  { key: 'result_4up', label: '4-Up' }
]

// Format date for compact display
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Computed properties - removed category and country filters

const uniqueDates = computed(() => {
  const dates = new Set(results.value.map(r => r.result_date))
  return Array.from(dates).sort()
})

const filteredTableData = computed(() => {
  // Filter out games with no results for the active tab type
  return tableData.value.filter(game => {
    // Check if game has at least one result for the active tab type
    return Object.values(game.results).some(dateResult => {
      // Only show games that have data for the current active tab
      return dateResult[activeTab.value] !== null && 
             dateResult[activeTab.value] !== undefined
    })
  })
})

// Methods
const fetchResults = async () => {
  try {
    // Cancel previous request if exists
    if (abortController) {
      abortController.abort()
    }
    
    // Create new abort controller
    abortController = new AbortController()
    
    loading.value = true
    error.value = ''
    const data = await gameApi.getAllResults(abortController.signal)
    results.value = data
    transformDataForTable(data)
  } catch (err: any) {
    // Don't show error if request was cancelled
    if (err.name !== 'AbortError') {
      error.value = 'Failed to fetch results'
      console.error('API Error:', err)
    }
  } finally {
    loading.value = false
  }
}

const transformDataForTable = (results: Result[]) => {
  const gameMap = new Map<number, TableData>()

  results.forEach(result => {
    if (!gameMap.has(result.game_id)) {
      gameMap.set(result.game_id, {
        gameName: result.game.game_name,
        gameId: result.game_id,
        results: {}
      })
    }

    const gameData = gameMap.get(result.game_id)!
    
    // Initialize date entry if not exists
    if (!gameData.results[result.result_date]) {
      gameData.results[result.result_date] = {
        result_2down: null,
        result_3up: null,
        result_4up: null,
        status: result.status,
        hasData: false
      }
    }
    
    const dateEntry = gameData.results[result.result_date]
    
    // Process each result type separately
    if (result.status === 'waiting') {
      dateEntry.result_2down = 'รอผล'
      dateEntry.result_3up = 'รอผล'
      dateEntry.result_4up = 'รอผล'
      dateEntry.hasData = true
    } else if (result.status === 'cancelled') {
      dateEntry.result_2down = 'ยกเลิก'
      dateEntry.result_3up = 'ยกเลิก'
      dateEntry.result_4up = 'ยกเลิก'
      dateEntry.hasData = true
    } else if (result.status === 'completed') {
      // Set individual result types
      dateEntry.result_2down = result.result_2down || null
      dateEntry.result_3up = result.result_3up || null
      dateEntry.result_4up = result.result_4up || null
      
      // Track if this game has data for future features
      dateEntry.hasData = !!(result.result_2down || result.result_3up || result.result_4up)
    }
  })

  tableData.value = Array.from(gameMap.values())
}

const getResultCellClass = (result: string | null | undefined) => {
  if (result === 'รอผล') {
    return 'text-yellow-500'
  } else if (result === 'ยกเลิก') {
    return 'text-red-500'
  } else if (!result) {
    return 'text-gray-400' // Lighter color for empty results
  }
  
  // Apply pattern highlighting only for 3-Up tab
  if (activeTab.value === 'result_3up' && result && result.length === 3) {
    const patternClass = getPatternClass(result)
    if (patternClass) {
      return `text-gray-900 ${patternClass}`
    }
  }
  
  return 'text-gray-900'
}

const getPatternClass = (result: string): string => {
  if (result.length !== 3) return ''
  
  const [d1, d2, d3] = result.split('')
  
  // Priority 1: All 3 digits same (111, 222, 333)
  if (d1 === d2 && d2 === d3) {
    return 'pattern-all-same'
  }
  
  // Priority 2: First 2 digits same (113, 225, 882)
  if (d1 === d2) {
    return 'pattern-first-two'
  }
  
  // Priority 3: Digit 1 & 3 same (040, 747, 202)
  if (d1 === d3) {
    return 'pattern-first-third'
  }
  
  // Priority 4: Last 2 digits same (200, 877, 399)
  if (d2 === d3) {
    return 'pattern-last-two'
  }
  
  return ''
}

// Lifecycle
onMounted(() => {
  fetchResults()
})

onUnmounted(() => {
  // Cancel any pending requests when component unmounts
  if (abortController) {
    abortController.abort()
  }
})
</script>

<style lang="scss" scoped>
$border-color: #d1d5db;
$hover-bg: #f9fafb;
$text-primary: #111827;
$text-secondary: #6b7280;
$text-muted: #9ca3af;

// Pattern highlighting colors - easy to customize
$pattern-all-same: #fecaca;     // Light red - highest priority
$pattern-first-two: #bfdbfe;    // Light blue
$pattern-first-third: #bbf7d0;  // Light green
$pattern-last-two: #fef3c7;     // Light yellow

// Table container with proper overflow settings
.table-container {
  overflow-x: auto;
  overflow-y: visible;
  max-height: 80vh;
}

.date-column {
  width: 40px;
  min-width: 40px;
  max-width: 40px;
}

// Sticky columns for horizontal scroll
.sticky-col-1 {
  position: sticky;
  left: 0;
  background-color: white;
  z-index: 10;
  min-width: 120px;
  max-width: 120px;
}

// Sticky header for vertical scroll - sticks to window top
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 20;
}

// Make all header cells sticky
.sticky-header th {
  position: sticky;
  top: 0;
  background-color: #f3f4f6;
}

// Header sticky columns
thead .sticky-col-1 {
  background-color: #f3f4f6;
  z-index: 30;
}

// Pattern highlighting classes
:deep(.pattern-all-same) {
  background-color: $pattern-all-same !important;
}

:deep(.pattern-first-two) {
  background-color: $pattern-first-two !important;
}

:deep(.pattern-first-third) {
  background-color: $pattern-first-third !important;
}

:deep(.pattern-last-two) {
  background-color: $pattern-last-two !important;
}

.results-table {
  th {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    color: $text-secondary;
    border-right: 1px solid $border-color;
    
    &:last-child {
      border-right: none;
    }
  }
  
  tr {
    &:hover {
      background-color: $hover-bg;
    }
    
    td {
      padding: 0.25rem 0.5rem;
      font-size: 0.75rem;
      
      &.result-cell {
        &.waiting {
          background-color: #fef3c7;
          color: #92400e;
        }
        
        &.cancelled {
          background-color: #fee2e2;
          color: #991b1b;
        }
        
        &.empty {
          color: $text-muted;
        }
      }
    }
  }
}
</style>