<template>
  <div>
    <!-- Loading Overlay -->
    <div v-if="props.gameOperationLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span>กำลังประมวลผล...</span>
      </div>
    </div>
    <!-- Target Digit Input -->
    <div class="bg-blue-50 p-4 rounded-lg mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">เลขเป้าหมาย</h3>
      <div class="flex items-center gap-3 mb-3">
        <label class="text-sm font-medium text-gray-700">เลข 1 หลัก:</label>
        <input 
          v-model="targetDigit" 
          type="text" 
          maxlength="1" 
          pattern="[0-9]"
          class="w-16 px-3 py-2 text-center text-xl border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="0"
        >
      </div>

    </div>
    
    <!-- Game Management -->
    <GameManager 
      :availableGames="availableGames" 
      :selectedGames="selectedGames"
      @addGame="handleAddGame"
      @reorderGames="handleReorderGames"
    />
    
    <!-- Game Results Preview -->
    <div v-if="selectedGames.length > 0" class="overflow-x-auto">
      <table class="min-w-full text-xs">
        <thead class="bg-gray-100">
          <tr>
            <th class="sticky-col-1 bg-gray-100 px-2 py-1 text-left font-medium text-gray-600">
              จัดการ
            </th>
            <th class="sticky-col-2 bg-gray-100 px-2 py-1 text-left font-medium text-gray-600">
              คิด
            </th>
            <th class="sticky-col-3 bg-gray-100 px-2 py-1 text-left font-medium text-gray-600">หวย</th>
            <th v-for="date in tableData.dates" :key="date.raw" class="px-2 py-1 text-center font-medium text-gray-600 border-r border-gray-300">
              {{ date.formatted }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white">
          <tr 
            v-for="gameData in tableData.games" 
            :key="gameData.game.id" 
            class="border-b border-gray-200"
          >
            <td class="sticky-col-1 bg-white px-2 py-1 text-center border-r border-gray-200">
              <button
                @click="removeGame(gameData.game.id)"
                class="text-red-600 hover:text-red-800 p-1"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z" />
                </svg>
              </button>
            </td>
            <td class="sticky-col-2 bg-white px-2 py-1 text-center border-r border-gray-200">
              <input
                v-model="gameData.calculate"
                type="checkbox"
                class="rounded"
                @change="handleCalculateChange"
              />
            </td>
            <td class="sticky-col-3 bg-white px-2 py-1 text-gray-900 border-r border-gray-200 truncate max-w-32">
              {{ gameData.game.game_name }}
            </td>
            <template v-for="date in tableData.dates" :key="date.raw">
              <td v-if="gameData.calculate" class="px-2 py-1 text-center border-r border-gray-200" :class="getCellClass(gameData.game.id, date.raw)">
                {{ getCellResult(gameData.game.id, date.raw) || '-' }}
              </td>
              <td v-else class="px-2 py-1 text-center border-r border-gray-200">
                <span class="text-gray-400">-</span>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Statistics Table -->
    <div v-if="selectedGames.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">สถิติการวิเคราะห์</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">หวย</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลทั้งหมด</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Match</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="gameData in gameStats" :key="gameData.game.id" class="hover:bg-gray-100">
              <td class="px-3 py-2 text-sm text-gray-900">{{ gameData.game.game_name }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ gameData.calculate ? gameData.totalResults : '-' }}</td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">{{ gameData.calculate ? gameData.matches : '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Game, Result } from '../types'
import GameManager from './GameManager.vue'

// Props
interface Props {
  allGames: Game[]
  allResults: Result[]
  gameMap: Map<number, Game> | null
  validResultsByGame: Map<number, Result[]> | null
  gameOperationLoading: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  gameOperationLoading: [value: boolean]
}>()

// Reactive state
const targetDigit = ref('')
const selectedGames = ref<{ game: Game, calculate: boolean }[]>([])

// Performance cache
const resultCache = new Map<string, Result | null>()
const cellCache = new Map<string, { result: string | null, cssClass: string }>()

// Computed properties
const availableGames = computed(() => {
  return props.allGames.filter(game => 
    !selectedGames.value.some(sg => sg.game.id === game.id)
  )
})

// Match counting
const matchCount = computed(() => {
  if (!targetDigit.value || selectedGames.value.length === 0) return 0
  
  const gameIds = selectedGames.value.map(g => g.game.id)
  return props.allResults
    .filter(r => gameIds.includes(r.game_id) && r.result_3up && r.status === 'completed')
    .filter(r => r.result_3up!.includes(targetDigit.value))
    .length
})

const totalResults = computed(() => {
  if (selectedGames.value.length === 0) return 0
  
  const gameIds = selectedGames.value.map(g => g.game.id)
  return props.allResults
    .filter(r => gameIds.includes(r.game_id) && r.result_3up && r.status === 'completed')
    .length
})

// Game statistics for table
const gameStats = computed(() => {
  return selectedGames.value.map(gameData => {
    const gameResults = props.allResults.filter(r => 
      r.game_id === gameData.game.id && r.result_3up && r.status === 'completed'
    )
    
    const matches = targetDigit.value 
      ? gameResults.filter(r => r.result_3up!.includes(targetDigit.value)).length
      : 0
    
    return {
      ...gameData,
      totalResults: gameResults.length,
      matches
    }
  })
})

// Game management event handlers
const handleAddGame = (gameId: number) => {
  if (!props.gameMap) return
  
  const game = props.gameMap.get(gameId)
  if (!game) return
  
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    selectedGames.value.push({ game, calculate: true })
    emit('gameOperationLoading', false)
  }, 0)
}

const handleReorderGames = (games: { game: Game }[]) => {
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    selectedGames.value = [...games]
    emit('gameOperationLoading', false)
  }, 0)
}

const removeGame = (gameId: number) => {
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    selectedGames.value = selectedGames.value.filter(g => g.game.id !== gameId)
    emit('gameOperationLoading', false)
  }, 0)
}

// Table data
const tableData = computed(() => {
  if (selectedGames.value.length === 0) return { dates: [], games: [] }
  
  const gameIds = selectedGames.value.map(g => g.game.id)
  const resultDates = Array.from(new Set(
    props.allResults
      .filter(r => gameIds.includes(r.game_id))
      .map(r => r.result_date)
  )).sort()
  
  // Generate complete date range if we have results
  let dates = resultDates
  if (resultDates.length > 1) {
    const startDate = new Date(resultDates[0])
    const endDate = new Date(resultDates[resultDates.length - 1])
    dates = []
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      dates.push(d.toISOString().split('T')[0])
    }
  }
  
  const formattedDates = dates.map(date => ({
    raw: date,
    formatted: new Date(date).toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' })
  }))
  
  return { dates: formattedDates, games: selectedGames.value }
})

// Optimized cell functions with caching
const getResult = (gameId: number, date: string) => {
  const key = `${gameId}-${date}`
  if (!resultCache.has(key)) {
    const result = props.allResults.find(r => r.game_id === gameId && r.result_date === date)
    resultCache.set(key, result || null)
  }
  return resultCache.get(key)
}

const getCellData = (gameId: number, date: string) => {
  const key = `${gameId}-${date}-${targetDigit.value}`
  
  if (!cellCache.has(key)) {
    const result = getResult(gameId, date)
    
    let cellResult: string | null = null
    let cssClass = 'text-gray-400'
    
    if (result) {
      if (result.status === 'waiting') {
        cellResult = 'รอผล'
        cssClass = 'text-yellow-600 bg-yellow-50'
      } else if (result.status === 'cancelled') {
        cellResult = 'ยกเลิก'
        cssClass = 'text-red-600 bg-red-50'
      } else if (result.result_3up) {
        cellResult = result.result_3up
        cssClass = targetDigit.value && result.result_3up.includes(targetDigit.value)
          ? 'text-gray-900 bg-green-200 font-medium'
          : 'text-gray-900'
      }
    }
    
    cellCache.set(key, { result: cellResult, cssClass })
  }
  
  return cellCache.get(key)!
}

const getCellResult = (gameId: number, date: string) => {
  return getCellData(gameId, date).result
}

const getCellClass = (gameId: number, date: string) => {
  return getCellData(gameId, date).cssClass
}

// Handle calculate checkbox changes with loading
const handleCalculateChange = () => {
  emit('gameOperationLoading', true)
  
  // Use longer timeout for heavy calculations
  setTimeout(() => {
    emit('gameOperationLoading', false)
  }, 100)
}

// Watch for input validation and clear cache
watch(targetDigit, (newValue) => {
  // Only allow single digit
  const cleaned = newValue.replace(/[^0-9]/g, '')
  if (cleaned !== newValue) {
    targetDigit.value = cleaned
  }
  // Clear cell cache when target digit changes
  cellCache.clear()
})
</script>

<style lang="scss" scoped>
// Sticky columns for horizontal scroll
.sticky-col-1 {
  position: sticky;
  left: 0;
  z-index: 10;
  width: 49px;
  min-width: 49px;
  max-width: 49px;
  border: 0;
}

.sticky-col-2 {
  position: sticky;
  left: 49px;
  z-index: 10;
  width: 32px;
  min-width: 32px;
  max-width: 32px;
  border: 0;
}

.sticky-col-3 {
  position: sticky;
  left: 81px;
  z-index: 10;
  width: 80px;
  min-width: 80px;
  max-width: 80px;
  border: 0;
}

@media (min-width: 768px) {
  .sticky-col-3 {
    min-width: 120px;
    max-width: 120px;
  }
}
</style>