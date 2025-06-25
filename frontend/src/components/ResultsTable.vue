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
      <!-- Category Filter -->
      <div class="mb-5">
        <label class="text-sm font-medium text-gray-700 mr-3">Filter by Category:</label>
        <select 
          v-model="selectedCategory"
          class="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <!-- Results Table -->
      <div class="overflow-x-auto border border-gray-200 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200">
                Game Name
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200">
                Category
              </th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200">
                Country
              </th>
              <th 
                v-for="date in uniqueDates" 
                :key="date"
                class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200 last:border-r-0"
              >
                {{ date }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="game in filteredTableData" :key="game.gameId" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm text-gray-900 border-r border-gray-200">
                {{ game.gameName }}
              </td>
              <td class="px-3 py-2 text-sm text-gray-900 border-r border-gray-200">
                {{ game.category }}
              </td>
              <td class="px-3 py-2 text-sm text-gray-900 border-r border-gray-200">
                {{ game.countryCode || '-' }}
              </td>
              <td 
                v-for="date in uniqueDates" 
                :key="date"
                class="px-3 py-2 text-sm text-center border-r border-gray-200 last:border-r-0"
                :class="getResultCellClass(game.results[date])"
              >
                {{ game.results[date] || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer Info -->
      <div class="mt-4 text-sm text-gray-600">
        Showing {{ filteredTableData.length }} games • Total results: {{ results.length }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { gameApi } from '../services/api'
import type { Result, TableData } from '../types'

// Reactive state
const results = ref<Result[]>([])
const tableData = ref<TableData[]>([])
const loading = ref(true)
const selectedCategory = ref('all')
const error = ref('')

// Computed properties
const categories = computed(() => {
  const cats = new Set(results.value.map(r => r.game.category))
  return Array.from(cats)
})

const uniqueDates = computed(() => {
  const dates = new Set(results.value.map(r => r.result_date))
  return Array.from(dates).sort()
})

const filteredTableData = computed(() => {
  return selectedCategory.value === 'all' 
    ? tableData.value 
    : tableData.value.filter(game => game.category === selectedCategory.value)
})

// Methods
const fetchResults = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await gameApi.getAllResults()
    results.value = data
    transformDataForTable(data)
  } catch (err) {
    error.value = 'Failed to fetch results'
    console.error('API Error:', err)
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
        category: result.game.category,
        countryCode: result.game.country_code,
        results: {}
      })
    }

    const gameData = gameMap.get(result.game_id)!
    
    // Format result display
    let resultDisplay = ''
    if (result.status === 'waiting') {
      resultDisplay = 'รอผล'
    } else if (result.status === 'cancelled') {
      resultDisplay = 'ยกเลิก'
    } else if (result.status === 'completed') {
      const parts = []
      if (result.result_3up) parts.push(result.result_3up)
      if (result.result_2down) parts.push(result.result_2down)
      if (result.result_4up) parts.push(result.result_4up)
      resultDisplay = parts.join('/') || '-'
    } else {
      resultDisplay = '-'
    }

    gameData.results[result.result_date] = resultDisplay
  })

  tableData.value = Array.from(gameMap.values())
}

const getResultCellClass = (result: string | undefined) => {
  if (result === 'รอผล') {
    return 'bg-yellow-100 text-yellow-800'
  } else if (result === 'ยกเลิก') {
    return 'bg-red-100 text-red-800'
  }
  return 'text-gray-900'
}

// Lifecycle
onMounted(() => {
  fetchResults()
})
</script>