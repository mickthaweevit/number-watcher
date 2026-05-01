<template>
  <div>
    <!-- Loading Overlay -->
    <div v-if="loading || profilesLoading || profileLoading || props.gameOperationLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span>{{ profileLoading ? 'กำลังโหลดโปรไฟล์...' : props.gameOperationLoading ? 'กำลังประมวลผล...' : 'Loading...' }}</span>
      </div>
    </div>

    <!-- Profile Management -->
    <div class="bg-green-50 p-4 rounded-lg mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">จัดการโปรไฟล์</h3>
      <div class="flex flex-wrap gap-3 mb-3">
        <select v-model="selectedProfileId" class="flex-1 px-3 py-2 border border-gray-300 rounded" :class="{ 'border-orange-400': hasUnsavedChanges }">
          <option :value="null">เลือกโปรไฟล์ที่บันทึก...</option>
          <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
            {{ profile.profile_name }} {{ hasUnsavedChanges && selectedProfileId === profile.id ? '*' : '' }}
          </option>
        </select>
        <button @click="saveCurrentProfile" :disabled="!canSaveCurrent" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400">
          บันทึก
        </button>
        <button @click="showSaveAsNewForm = true" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
          บันทึกโปรไฟล์ใหม่
        </button>
        <button @click="deleteProfile" :disabled="!selectedProfileId" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400">
          ลบ
        </button>
      </div>
    </div>
    
    <!-- Game Management -->
    <GameManager 
      :availableGames="availableGames" 
      :selectedGames="selectedGames"
      @addGame="handleAddGame"
      @addMultipleGames="handleAddMultipleGames"
      @reorderGames="handleReorderGames"
    />
      
      <!-- Game Results Preview -->
    <div v-if="selectedGames.length > 0" class="overflow-x-auto" ref="previewTableContainer">
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
            <th v-for="date in baseTableData.dates" :key="date.raw" class="px-2 py-1 text-center font-medium text-gray-600 border-r border-gray-300">
              {{ date.formatted }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white">
          <tr 
            v-for="(gameAnalysis, index) in baseTableData.games" 
            :key="gameAnalysis.game.id" 
            class="border-b border-gray-200"
          >
            <td class="sticky-col-1 bg-white px-2 py-1 text-center border-r border-gray-200">
              <button
                @click="removeGame(gameAnalysis.game.id)"
                class="text-red-600 hover:text-red-800 p-1"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z" />
                </svg>
              </button>
            </td>
            <td class="sticky-col-2 bg-white px-2 py-1 text-center border-r border-gray-200">
              <input
                v-model="gameAnalysis.calculate"
                type="checkbox"
                class="rounded"
              />
            </td>
            <td class="sticky-col-3 bg-white px-2 py-1 text-gray-900 border-r border-gray-200 truncate max-w-32">
              {{ gameAnalysis.game.game_name }}
            </td>
            <template v-for="date in baseTableData.dates" :key="date.raw">
              <td v-if="gameAnalysis.calculate" class="px-2 py-1 text-center border-r border-gray-200" :class="getCellData(gameAnalysis.game.id, date.raw).cssClass">
                {{ getCellData(gameAnalysis.game.id, date.raw).result || '-' }}
              </td>
              <td v-else class="px-2 py-1 text-center border-r border-gray-200">
                <span class="text-gray-400">-</span>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pattern Highlighting Controls -->
    <PatternSelector 
      v-model:selectedPatterns="selectedPatterns" 
      :availablePatterns="availablePatterns" 
    />

    <!-- Monthly Pattern Statistics -->
    <div v-if="selectedGames.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">สถิติรายเดือน</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เดือน</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">หน้า</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">หาม</th>
              <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">หลัง</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="monthStat in monthlyPatternStats" :key="monthStat.month" class="hover:bg-gray-50">
              <td class="px-3 py-2 text-sm text-gray-900">{{ monthStat.monthFormatted }}</td>
              <td class="px-3 py-2 text-sm text-center text-gray-900">{{ monthStat.firstTwo }}</td>
              <td class="px-3 py-2 text-sm text-center text-gray-900">{{ monthStat.firstThird }}</td>
              <td class="px-3 py-2 text-sm text-center text-gray-900">{{ monthStat.lastTwo }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Statistic Table -->
    <div v-if="selectedGames.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">การวิเคราะห์หวยที่เลือก</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">หวย</th>
              <th class="px-1 py-2 text-left text-xs font-medium text-gray-500 uppercase w-16">เบิ้ลหน้า</th>
              <th class="px-1 py-2 text-left text-xs font-medium text-gray-500 uppercase w-16">หาม</th>
              <th class="px-1 py-2 text-left text-xs font-medium text-gray-500 uppercase w-16">เบิ้ลหลัง</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลทั้งหมด</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">รูปแบบตรง</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่ได้</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่เสีย</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลรวม</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase"> </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <template v-for="gameAnalysis in selectedGames" :key="gameAnalysis.game.id">
              <tr class="hover:bg-gray-100">
                <td class="px-3 py-2 text-sm text-gray-900">{{ gameAnalysis.game.game_name }}</td>
                <td class="px-1 py-2 text-sm text-gray-900 bg-blue-100">
                  <input 
                    v-model.number="gameAnalysis.patterns.first_two.betAmount" 
                    type="number" 
                    min="0" 
                    placeholder="0"
                    class="w-12 px-1 py-1 text-xs border rounded"
                    @input="recalculateGame(gameAnalysis)"
                  >
                </td>
                <td class="px-1 py-2 text-sm text-gray-900 bg-green-100">
                  <input 
                    v-model.number="gameAnalysis.patterns.first_third.betAmount" 
                    type="number" 
                    min="0" 
                    placeholder="0"
                    class="w-12 px-1 py-1 text-xs border rounded"
                    @input="recalculateGame(gameAnalysis)"
                  >
                </td>
                <td class="px-1 py-2 text-sm text-gray-900 bg-yellow-100">
                  <input 
                    v-model.number="gameAnalysis.patterns.last_two.betAmount" 
                    type="number" 
                    min="0" 
                    placeholder="0"
                    class="w-12 px-1 py-1 text-xs border rounded"
                    @input="recalculateGame(gameAnalysis)"
                  >
                </td>
                <td class="px-3 py-2 text-sm text-gray-600">
                  {{ gameAnalysis.calculate ? gameAnalysis.totalResults : '-' }}
                </td>
                <td class="px-3 py-2 text-sm">
                  <span v-if="gameAnalysis.calculate" :class="getMatchClass(getTotalWins(gameAnalysis))">
                    {{ getTotalWins(gameAnalysis) }}
                  </span>
                  <span v-else class="text-gray-400">-</span>
                </td>
                <td class="px-3 py-2 text-sm text-green-600 font-medium">
                  {{ gameAnalysis.calculate ? formatCurrency(getTotalWinAmount(gameAnalysis)) : '-' }}
                </td>
                <td class="px-3 py-2 text-sm text-red-600 font-medium">
                  {{ gameAnalysis.calculate ? formatCurrency(getTotalLossAmount(gameAnalysis)) : '-' }}
                </td>
                <td class="px-3 py-2 text-sm font-medium" :class="getNetClass(getTotalNetAmount(gameAnalysis))">
                  {{ gameAnalysis.calculate ? formatCurrency(getTotalNetAmount(gameAnalysis)) : '-' }}
                </td>
                <td class="px-3 py-2 text-sm font-medium">
                  <button @click="toggleRowExpansion(gameAnalysis.game.id)" class="p-1 hover:bg-gray-100 rounded">
                    <svg class="w-4 h-4 transition-transform" :class="{ 'rotate-180': expandedRows.has(gameAnalysis.game.id) }" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                    </svg>
                  </button>
                </td>
              </tr>
              <!-- Expandable row -->
              <tr v-if="expandedRows.has(gameAnalysis.game.id)" class="bg-gray-50">
                <td colspan="10" class="px-3 py-4">
                  <div class="text-sm font-medium text-gray-700 mb-2">
                    รายละเอียดรายเดือน
                  </div>
                  <div class="overflow-x-auto">
                    <table class="min-w-full text-xs">
                      <thead>
                        <tr class="bg-gray-100">
                          <th rowspan="2" class="px-2 py-1 text-left font-medium text-gray-600">เดือน</th>
                          <th colspan="2" class="px-2 py-1 text-center font-medium text-gray-600 bg-blue-100">เบิ้ลหน้า</th>
                          <th colspan="2" class="px-2 py-1 text-center font-medium text-gray-600 bg-green-100">หาม</th>
                          <th colspan="2" class="px-2 py-1 text-center font-medium text-gray-600 bg-yellow-100">เบิ้ลหลัง</th>
                          <th colspan="2" class="px-2 py-1 text-center font-medium text-gray-600">ทั้งหมด</th>
                          <th rowspan="2" class="px-2 py-1 text-right font-medium text-gray-600">ผลรวม</th>
                          <th rowspan="2" class="px-2 py-1 text-center font-medium text-gray-600">%</th>
                        </tr>
                        <tr class="bg-gray-100">
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-blue-100">ถูก</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-blue-100">รวม</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-green-100">ถูก</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-green-100">รวม</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-yellow-100">ถูก</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600 bg-yellow-100">รวม</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600">ถูก</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600">รวม</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="monthData in getGameMonthlyData(gameAnalysis.game.id)" :key="monthData.month" class="border-b border-gray-200">
                          <!-- <td colspan="5">{{ monthData }}</td> -->
                          <td class="px-2 py-1 text-gray-700">{{ formatMonth(monthData.month) }}</td>

                          <td class="px-2 py-1 text-center text-green-600">{{ monthData.firstTwo.wins }}</td>
                          <td class="px-2 py-1 text-center text-gray-600">{{ monthData.firstTwo.wins + monthData.firstTwo.losses }}</td>

                          <td class="px-2 py-1 text-center text-green-600">{{ monthData.firstThird.wins }}</td>
                          <td class="px-2 py-1 text-center text-gray-600">{{ monthData.firstThird.wins + monthData.firstThird.losses }}</td>

                          <td class="px-2 py-1 text-center text-green-600">{{ monthData.lastTwo.wins }}</td>
                          <td class="px-2 py-1 text-center text-gray-600">{{ monthData.lastTwo.wins + monthData.lastTwo.losses }}</td>

                          <td class="px-2 py-1 text-center text-green-600">{{ monthData.allWins }}</td>
                          <td class="px-2 py-1 text-center text-gray-600">{{ monthData.allWins + monthData.allLosses }}</td>
                          <td class="px-2 py-1 text-right font-medium" :class="getNetClass(monthData.netAmount)">{{ formatCurrency(monthData.netAmount) }}</td>
                          <td class="px-2 py-1 text-center text-gray-600">{{ getWinRate(monthData.allWins, monthData.allLosses) }}%</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Statistics Summary -->
    <StatisticsPanel 
      :totalStats="totalStats"
      :monthlyStats="monthlyStats"
      :formatCurrency="formatCurrency"
      :getNetClass="getNetClass"
    />

    <!-- Save as New Profile Modal -->
    <div v-if="showSaveAsNewForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">บันทึกโปรไฟล์ใหม่</h3>
        <form @submit.prevent="saveAsNewProfile">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">ชื่อโปรไฟล์</label>
            <input v-model="newProfileName" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="กรอกชื่อโปรไฟล์">
          </div>
          <div class="flex gap-3">
            <button type="submit" class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              บันทึก
            </button>
            <button type="button" @click="showSaveAsNewForm = false; newProfileName = ''" class="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
              ยกเลิก
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { gameApi, authApi, profileApi } from '../services/api'
import type { Game, Result, User, DashboardProfile } from '../types'
import { useGameAnalysis, type GameAnalysis } from '../composables/useGameAnalysis'
import { useProfileManagement } from '../composables/useProfileManagement'
import PatternSelector from './PatternSelector.vue'
import GameManager from './GameManager.vue'
import StatisticsPanel from './StatisticsPanel.vue'

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
const betAmount = ref(10) // Default bet amount
const selectedPatterns = ref<string[]>([])
const selectedGames = ref<GameAnalysis[]>([])
const loading = ref(false)

// Expandable rows state
const expandedRows = ref<Set<number>>(new Set())

// User state (always logged in now)
const user = ref<User | null>(null)

// Profile UI state
const showSaveAsNewForm = ref(false)
const newProfileName = ref('')

// Pattern definitions with count information
const availablePatterns = [
  { key: 'first_two', label: 'เบิ้ลหน้า', colorClass: 'bg-blue-100', count: 90 },
  { key: 'first_third', label: 'หาม', colorClass: 'bg-green-100', count: 90 },
  { key: 'last_two', label: 'เบิ้ลหลัง', colorClass: 'bg-yellow-100', count: 90 }
]

// Use composables
const {
  analysisCache,
  analyzeGameOptimized,
  recalculateGame,
  getTotalWins,
  getTotalWinAmount,
  getTotalLossAmount,
  getTotalNetAmount,
  getMonthlyData
} = useGameAnalysis()

const {
  profiles,
  selectedProfileId,
  profilesLoading,
  profileLoading,
  hasUnsavedChanges,
  canSaveCurrent,
  fetchProfiles,
  saveCurrentProfile: saveCurrentProfileComposable,
  saveAsNewProfile: saveAsNewProfileComposable,
  deleteProfile: deleteProfileComposable,
  updateLoadedState,
  checkForUnsavedChanges,
  clearProfile,
  cancelProfileLoad,
  loadedProfileState,
  setLoadProfileAbortController,
  setProfileLoading
} = useProfileManagement()

// Computed properties
const availableGames = computed(() => {
  return props.allGames.filter(game => 
    !selectedGames.value.some(sg => sg.game.id === game.id)
  )
})

const totalStats = computed(() => {
  const calculatedGames = selectedGames.value.filter(g => g.calculate)
  return {
    games: calculatedGames.length,
    results: calculatedGames.reduce((sum, g) => sum + g.totalResults, 0),
    wins: calculatedGames.reduce((sum, g) => sum + getTotalWins(g), 0),
    losses: calculatedGames.reduce((sum, g) => sum + (g.totalResults - getTotalWins(g)), 0),
    netAmount: calculatedGames.reduce((sum, g) => sum + getTotalNetAmount(g), 0)
  }
})

// Consolidated monthly data computation to avoid duplicate getMonthlyData calls
const consolidatedMonthlyData = computed(() => {
  const monthlyStats: { [month: string]: { wins: number, losses: number, netAmount: number } } = {}
  const monthlyPatterns: { [month: string]: { firstTwo: number, firstThird: number, lastTwo: number } } = {}
  
  selectedGames.value.filter(g => g.calculate).forEach(game => {
    const gameMonthlyData = getMonthlyData(game) // Single call per game
    
    gameMonthlyData.forEach(monthInfo => {
      // Initialize if not exists
      if (!monthlyStats[monthInfo.month]) {
        monthlyStats[monthInfo.month] = { wins: 0, losses: 0, netAmount: 0 }
        monthlyPatterns[monthInfo.month] = { firstTwo: 0, firstThird: 0, lastTwo: 0 }
      }
      
      // Aggregate stats
      monthlyStats[monthInfo.month].wins += monthInfo.allWins
      monthlyStats[monthInfo.month].losses += monthInfo.allLosses
      monthlyStats[monthInfo.month].netAmount += monthInfo.netAmount
      
      // Aggregate patterns
      monthlyPatterns[monthInfo.month].firstTwo += monthInfo.firstTwo.wins
      monthlyPatterns[monthInfo.month].firstThird += monthInfo.firstThird.wins
      monthlyPatterns[monthInfo.month].lastTwo += monthInfo.lastTwo.wins
    })
  })
  
  return { monthlyStats, monthlyPatterns }
})

const monthlyStats = computed(() => {
  return Object.entries(consolidatedMonthlyData.value.monthlyStats)
    .map(([month, data]) => ({ month, ...data }))
    .sort((a, b) => a.month.localeCompare(b.month))
})

const monthlyPatternStats = computed(() => {
  return Object.entries(consolidatedMonthlyData.value.monthlyPatterns)
    .map(([month, data]) => ({
      month,
      monthFormatted: formatMonthShort(month),
      ...data
    }))
    .sort((a, b) => a.month.localeCompare(b.month))
})

// Game management event handlers
const handleAddGame = (gameId: number) => {
  if (!props.gameMap || !props.validResultsByGame) return
  
  const game = props.gameMap.get(gameId)
  if (!game) return
  
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    const gameResults = props.validResultsByGame!.get(gameId) || []
    const analysis = analyzeGameOptimized(game, gameResults)
    
    selectedGames.value.push(analysis)
    emit('gameOperationLoading', false)
  }, 0)
}

const handleAddMultipleGames = (gameIds: number[]) => {
  if (!props.gameMap || !props.validResultsByGame) return
  
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    gameIds.forEach(gameId => {
      const game = props.gameMap!.get(gameId)
      if (game) {
        const gameResults = props.validResultsByGame!.get(gameId) || []
        const analysis = analyzeGameOptimized(game, gameResults)
        selectedGames.value.push(analysis)
      }
    })
    emit('gameOperationLoading', false)
  }, 0)
}

const handleReorderGames = (games: GameAnalysis[]) => {
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

const formatCurrency = (amount: number): string => {
  return amount.toLocaleString()
}

const getMatchClass = (matches: number): string => {
  return matches > 0 ? 'text-green-600 font-medium' : 'text-gray-600'
}

const getNetClass = (amount: number): string => {
  if (amount > 0) return 'text-green-600'
  if (amount < 0) return 'text-red-600'
  return 'text-gray-600'
}

// Profile methods using composable
const saveCurrentProfile = async () => {
  await saveCurrentProfileComposable(selectedPatterns.value, selectedGames.value)
}

const saveAsNewProfile = async () => {
  const success = await saveAsNewProfileComposable(newProfileName.value, selectedPatterns.value, selectedGames.value)
  if (success) {
    showSaveAsNewForm.value = false
    newProfileName.value = ''
  }
}

const deleteProfile = async () => {
  await deleteProfileComposable()
}

const loadProfile = async () => {
  if (!selectedProfileId.value || !props.gameMap || !props.validResultsByGame) return
  
  cancelProfileLoad()
  const abortController = new AbortController()
  setLoadProfileAbortController(abortController)
  setProfileLoading(true)
  
  try {
    const profile = profiles.value.find(p => p.id === selectedProfileId.value)
    if (!profile || abortController.signal.aborted) return
    
    selectedPatterns.value = [...profile.selected_patterns]
    await new Promise(resolve => setTimeout(resolve, 0))
    
    selectedGames.value = profile.selected_game_ids
      .map(gameId => {
        const game = props.gameMap!.get(gameId)
        if (!game) return null
        
        const analysis = analyzeGameOptimized(game, props.validResultsByGame!.get(gameId) || [])
        
        const savedBets = (profile as any).game_pattern_bets?.[gameId]
        if (savedBets) {
          analysis.patterns.first_two.betAmount = savedBets.first_two || 0
          analysis.patterns.first_third.betAmount = savedBets.first_third || 0
          analysis.patterns.last_two.betAmount = savedBets.last_two || 0
          recalculateGame(analysis)
        }
        
        return analysis
      })
      .filter(Boolean)
    
    updateLoadedState(selectedPatterns.value, selectedGames.value)
    
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('Profile load error:', error)
    }
  } finally {
    setProfileLoading(false)
    setLoadProfileAbortController(null)
  }
}

// Base table data (doesn't change with patterns)
const baseTableData = computed(() => {
  if (selectedGames.value.length === 0) return { dates: [], games: [], cells: {} }
  
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
  
  const cells: { [key: string]: { result: string | null, baseClass: string } } = {}
  
  selectedGames.value.forEach(gameAnalysis => {
    dates.forEach(date => {
      const key = `${gameAnalysis.game.id}-${date}`
      const result = props.allResults.find(r => r.game_id === gameAnalysis.game.id && r.result_date === date)
      
      let cellResult: string | null = null
      let baseClass = 'text-gray-400'
      
      if (result) {
        if (result.status === 'waiting') {
          cellResult = 'รอผล'
          baseClass = 'text-yellow-600 bg-yellow-50'
        } else if (result.status === 'cancelled') {
          cellResult = 'ยกเลิก'
          baseClass = 'text-red-600 bg-red-50'
        } else if (result.result_3up) {
          cellResult = result.result_3up
          baseClass = 'text-gray-900'
        }
      }
      
      cells[key] = { result: cellResult, baseClass }
    })
  })
  
  return { dates: formattedDates, games: selectedGames.value, cells }
})

// Pattern classes (only recalculates when patterns change)
const patternClasses = computed(() => {
  const classes: { [key: string]: string } = {}
  
  Object.entries(baseTableData.value.cells).forEach(([key, cell]) => {
    if (cell.result && cell.result.length === 3 && cell.baseClass === 'text-gray-900') {
      const [d1, d2, d3] = cell.result.split('')
      
      if (selectedPatterns.value.includes('all_same') && d1 === d2 && d2 === d3) {
        classes[key] = 'bg-red-100'
      } else if (selectedPatterns.value.includes('first_two') && d1 === d2 && d2 !== d3) {
        classes[key] = 'bg-blue-100'
      } else if (selectedPatterns.value.includes('first_third') && d1 === d3 && d1 !== d2) {
        classes[key] = 'bg-green-100'
      } else if (selectedPatterns.value.includes('last_two') && d2 === d3 && d1 !== d2) {
        classes[key] = 'bg-yellow-100'
      }
    }
  })
  
  return classes
})

// Helper function to get cell data with pattern highlighting
const getCellData = (gameId: number, date: string) => {
  const key = `${gameId}-${date}`
  const baseCell = baseTableData.value.cells[key] || { result: null, baseClass: 'text-gray-400' }
  const patternClass = patternClasses.value[key] || ''
  
  return {
    result: baseCell.result,
    cssClass: patternClass ? `${baseCell.baseClass} ${patternClass}` : baseCell.baseClass
  }
}

// Expandable rows functions
const toggleRowExpansion = (gameId: number) => {
  if (expandedRows.value.has(gameId)) {
    expandedRows.value.delete(gameId)
  } else {
    expandedRows.value.add(gameId)
  }
}

// Cache for game monthly data to avoid recalculation
const gameMonthlyDataCache = computed(() => {
  const cache: { [gameId: number]: any[] } = {}
  selectedGames.value.forEach(game => {
    if (game.calculate) {
      cache[game.game.id] = getMonthlyData(game)
    }
  })
  return cache
})

// Helper function to get monthly data for a specific game
const getGameMonthlyData = (gameId: number) => {
  return gameMonthlyDataCache.value[gameId] || []
}

const formatMonth = (month: string) => {
  const [year, monthNum] = month.split('-')
  const monthNames = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
  return `${monthNames[parseInt(monthNum) - 1]} ${year}`
}

const formatMonthShort = (month: string) => {
  const [year, monthNum] = month.split('-')
  return `${monthNum.padStart(2, '0')}/${year.slice(-2)}`
}

const getWinRate = (wins: number, losses: number) => {
  const total = wins + losses
  return total > 0 ? Math.round((wins / total) * 100) : 0
}

// Watch for profile selection changes - auto load
watch(selectedProfileId, (newProfileId) => {
  if (newProfileId) {
    loadProfile()
  } else {
    selectedGames.value = []
    betAmount.value = 10
    selectedPatterns.value = []
    clearProfile()
  }
})

// Watch for changes in bet amount or patterns with debouncing
watch([betAmount, selectedPatterns], () => {
  analysisCache.clear() // Clear cache when settings change
  recalculateAllGames()
}, { deep: true })

// Recalculate all games when patterns change
const recalculateAllGames = () => {
  if (!props.validResultsByGame) return
  
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    selectedGames.value.forEach(gameAnalysis => {
      if (gameAnalysis.calculate) {
        const gameResults = props.validResultsByGame!.get(gameAnalysis.game.id) || []
        const newAnalysis = analyzeGameOptimized(gameAnalysis.game, gameResults)
        // Preserve bet amounts
        newAnalysis.patterns.first_two.betAmount = gameAnalysis.patterns.first_two.betAmount
        newAnalysis.patterns.first_third.betAmount = gameAnalysis.patterns.first_third.betAmount
        newAnalysis.patterns.last_two.betAmount = gameAnalysis.patterns.last_two.betAmount
        recalculateGame(newAnalysis)
        Object.assign(gameAnalysis, newAnalysis)
      }
    })
    emit('gameOperationLoading', false)
  }, 0)
}

// Track unsaved changes
watch([betAmount, selectedPatterns, selectedGames], () => {
  if (selectedProfileId.value && loadedProfileState.value) {
    hasUnsavedChanges.value = checkForUnsavedChanges(selectedPatterns.value, selectedGames.value)
  }
}, { deep: true })

// Template ref
const previewTableContainer = ref<HTMLElement | null>(null)

// Auto-scroll to right when results load
watch(() => baseTableData.value.dates.length, (newLength) => {
  if (newLength > 0) {
    nextTick(() => {
      const container = previewTableContainer.value
      if (container) {
        container.scrollLeft = container.scrollWidth
      }
    })
  }
})

// Initialize
onMounted(async () => {
  try {
    user.value = await authApi.getCurrentUser()
    await fetchProfiles()
  } catch (error) {
    console.error('Failed to get user:', error)
  }
})
</script>

<style lang="scss" scoped>
select:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

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