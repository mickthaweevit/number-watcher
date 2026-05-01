<template>
  <div>
    <!-- Loading Overlay -->
    <div v-if="props.gameOperationLoading || profileLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span>{{ profileLoading ? 'กำลังโหลดโปรไฟล์...' : 'กำลังประมวลผล...' }}</span>
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

    <!-- Target Digits Selection -->
    <div class="bg-blue-50 p-4 rounded-lg mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">เลขเป้าหมาย</h3>
      
      <!-- Match Method Selection -->
      <div class="mb-4">
        <label class="text-sm font-medium text-gray-700 mb-2 block">วิธีการตรวจสอบ:</label>
        <div class="flex flex-wrap gap-4">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input v-model="matchMethod" value="OR" type="radio" class="rounded">
            <span>OR (มีเลขใดเลขหนึ่ง)</span>
          </label>
          <label class="flex items-center space-x-2 cursor-pointer">
            <input v-model="matchMethod" value="AND" type="radio" class="rounded">
            <span>AND (มีเลขทุกตัว สูงสุด 3 ตัว)</span>
          </label>
          <label class="flex items-center space-x-2 cursor-pointer">
            <input v-model="noDuplicate" type="checkbox" class="rounded">
            <span>ตัดเบิ้ล (ไม่มีเลขซ้ำ)</span>
          </label>
        </div>
      </div>
      
      <!-- Digit Selection -->
      <div class="grid grid-cols-5 gap-3 mb-4">
        <label v-for="digit in [0,1,2,3,4,5,6,7,8,9]" :key="digit" class="flex items-center space-x-2 cursor-pointer">
          <input 
            v-model="targetDigits" 
            :value="digit.toString()"
            type="checkbox"
            class="rounded"
            :disabled="matchMethod === 'AND' && targetDigits.length >= 3 && !targetDigits.includes(digit.toString())"
          >
          <span class="text-lg font-medium" :class="{ 'text-gray-400': matchMethod === 'AND' && targetDigits.length >= 3 && !targetDigits.includes(digit.toString()) }">เลข {{ digit }}</span>
        </label>
      </div>
      
      <!-- Bet Numbers -->
      <div class="flex items-center gap-3 mb-4">
        <span class="text-sm font-medium text-gray-700">จำนวนตัวเลขทั้งหมด</span>
        <span class="font-medium text-orange-600">{{ betNumbersData.count }}</span>
        <span class="text-sm text-gray-600">เลข</span>
        <button 
          v-if="betNumbersData.count > 0"
          @click="showBetNumbersDialog = true" 
          class="ml-2 p-1 text-gray-500 hover:text-blue-600 transition-colors"
          title="ดูตัวเลขที่เดิมพัน"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z" />
          </svg>
        </button>
      </div>

      <!-- Bet Amount -->
      <div class="flex items-center gap-3">
        <label class="text-sm font-medium text-gray-700">จำนวนเงินเดิมพัน:</label>
        <input 
          v-model.number="betAmount" 
          type="number" 
          min="1" 
          class="w-24 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="10"
        >
        <span class="text-sm text-gray-600">บาท</span>
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
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่ได้</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่เสีย</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลรวม</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="gameData in gameStats" :key="gameData.game.id" class="hover:bg-gray-100">
              <td class="px-3 py-2 text-sm text-gray-900">{{ gameData.game.game_name }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ gameData.calculate ? gameData.totalResults : '-' }}</td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">{{ gameData.calculate ? gameData.matches : '-' }}</td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">{{ gameData.calculate ? formatCurrency(gameData.winAmount) : '-' }}</td>
              <td class="px-3 py-2 text-sm text-red-600 font-medium">{{ gameData.calculate ? formatCurrency(gameData.lossAmount) : '-' }}</td>
              <td class="px-3 py-2 text-sm font-medium" :class="getNetClass(gameData.netAmount)">{{ gameData.calculate ? formatCurrency(gameData.netAmount) : '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Monthly Statistics -->
    <div v-if="selectedGames.length > 0 && monthlyStats.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">สถิติรายเดือน</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เดือน</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ถูก</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลทั้งหมด</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่ได้</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">เงินที่เสีย</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ผลรวม</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">%</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="monthData in monthlyStats" :key="monthData.month" class="hover:bg-gray-100">
              <td class="px-3 py-2 text-sm text-gray-900">{{ formatMonth(monthData.month) }}</td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">{{ monthData.wins }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ monthData.wins + monthData.losses }}</td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">{{ formatCurrency(monthData.winAmount) }}</td>
              <td class="px-3 py-2 text-sm text-red-600 font-medium">{{ formatCurrency(monthData.lossAmount) }}</td>
              <td class="px-3 py-2 text-sm font-medium" :class="getNetClass(monthData.netAmount)">{{ formatCurrency(monthData.netAmount) }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ getWinRate(monthData.wins, monthData.losses) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Summary Statistics -->
    <div v-if="selectedGames.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">สรุปรวม</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ totalStats.games }}</div>
          <div class="text-sm text-gray-600">หวยที่คิด</div>
        </div>
        <div class="bg-green-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ totalStats.wins }}</div>
          <div class="text-sm text-gray-600">ถูกทั้งหมด</div>
        </div>
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-black-600">{{ totalStats.wins + totalStats.losses }}</div>
          <div class="text-sm text-gray-600">ผลทั้งหมด</div>
        </div>
        <div class="bg-purple-50 p-4 rounded-lg">
          <div class="text-2xl font-bold" :class="getNetClass(totalStats.netAmount)">{{ formatCurrency(totalStats.netAmount) }}</div>
          <div class="text-sm text-gray-600">ผลรวมสุทธิ</div>
        </div>
      </div>
    </div>
    
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
    
    <!-- Bet Numbers Dialog -->
    <div v-if="showBetNumbersDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold">ตัวเลขที่เดิมพัน ({{ betNumbersData.count }} ตัว)</h3>
          <button @click="showBetNumbersDialog = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
            </svg>
          </button>
        </div>
        <div class="overflow-y-auto max-h-[80vh]">
          <div class="grid grid-cols-3 md:grid-cols-6 lg:grid-cols-10 gap-2 text-lg">
            <span v-for="number in betNumbersData.numbers" :key="number" class="px-2 py-1 bg-gray-100 rounded text-center font-mono">
              {{ number }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import type { Game, Result } from '../types'
import { useProfileManagement } from '../composables/useProfileManagement'
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
const matchMethod = ref('OR')
const targetDigits = ref<string[]>([])
const selectedGames = ref<{ game: Game, calculate: boolean }[]>([])
const betAmount = ref(10)
const noDuplicate = ref(false)

// Profile UI state
const showSaveAsNewForm = ref(false)
const newProfileName = ref('')
const showBetNumbersDialog = ref(false)

// Use profile management composable
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
  clearProfile,
  loadedProfileState
} = useProfileManagement()

// Performance cache
const resultCache = new Map<string, Result | null>()
const cellCache = new Map<string, { result: string | null, cssClass: string }>()

// Computed properties
const availableGames = computed(() => {
  return props.allGames.filter(game => 
    !selectedGames.value.some(sg => sg.game.id === game.id)
  )
})



// Helper function to check if number has duplicate digits
const hasDuplicateDigits = (numStr: string) => {
  const digits = numStr.split('')
  return new Set(digits).size !== digits.length
}

// Calculate how many numbers to bet on based on method and digits
const betNumbersData = computed(() => {
  if (targetDigits.value.length === 0) return { count: 0, numbers: [] }
  
  let numbers: string[] = []
  
  if (matchMethod.value === 'OR') {
    // OR: Bet on every number that has ANY of the selected digits
    const digitSet = new Set(targetDigits.value)
    
    for (let i = 0; i <= 999; i++) {
      const numStr = i.toString().padStart(3, '0')
      const hasAnyDigit = numStr.split('').some(d => digitSet.has(d))
      if (hasAnyDigit) numbers.push(numStr)
    }
  } else {
    // AND: Bet on every number that has ALL of the selected digits
    const digits = targetDigits.value
    
    for (let i = 0; i <= 999; i++) {
      const numStr = i.toString().padStart(3, '0')
      const hasAllDigits = digits.every(digit => numStr.includes(digit))
      if (hasAllDigits) numbers.push(numStr)
    }
  }
  
  // Filter out duplicates if noDuplicate is checked
  if (noDuplicate.value) {
    numbers = numbers.filter(numStr => !hasDuplicateDigits(numStr))
  }
  
  return { count: numbers.length, numbers }
})

// Game statistics for table with financial calculations
const gameStats = computed(() => {
  
  return selectedGames.value.map(gameData => {
    const gameResults = props.allResults.filter(r => 
      r.game_id === gameData.game.id && r.result_3up && r.status === 'completed'
    )
    
    const matches = targetDigits.value.length > 0
      ? gameResults.filter(r => checkMatch(r.result_3up!)).length
      : 0
    
    // Financial calculations based on actual betting numbers
    const winAmount = matches * betAmount.value * 1000 // 1000x payout per winning number
    const lossAmount = gameResults.length * betAmount.value * betNumbersData.value.count // Cost per draw = bet × numbers bet on
    const netAmount = winAmount - lossAmount
    
    return {
      ...gameData,
      totalResults: gameResults.length,
      matches,
      winAmount,
      lossAmount,
      netAmount,
      betNumbersCount: betNumbersData.value.count
    }
  })
})

// Monthly statistics
const monthlyStats = computed(() => {
  if (selectedGames.value.length === 0 || targetDigits.value.length === 0) return []
  
  const monthlyData: { [month: string]: { wins: number, losses: number, winAmount: number, lossAmount: number } } = {}
  
  selectedGames.value.filter(g => g.calculate).forEach(gameData => {
    const gameResults = props.allResults.filter(r => 
      r.game_id === gameData.game.id && r.result_3up && r.status === 'completed'
    )
    
    gameResults.forEach(result => {
      const month = result.result_date.substring(0, 7) // YYYY-MM
      
      if (!monthlyData[month]) {
        monthlyData[month] = { wins: 0, losses: 0, winAmount: 0, lossAmount: 0 }
      }
      
      const isMatch = checkMatch(result.result_3up!)
      if (isMatch) {
        monthlyData[month].wins += 1
        monthlyData[month].winAmount += betAmount.value * 1000
      } else {
        monthlyData[month].losses += 1
      }
      monthlyData[month].lossAmount += betAmount.value * betNumbersData.value.count
    })
  })
  
  return Object.entries(monthlyData)
    .map(([month, data]) => ({
      month,
      wins: data.wins,
      losses: data.losses,
      winAmount: data.winAmount,
      lossAmount: data.lossAmount,
      netAmount: data.winAmount - data.lossAmount
    }))
    .sort((a, b) => a.month.localeCompare(b.month))
})

// Total statistics
const totalStats = computed(() => {
  const calculatedGames = selectedGames.value.filter(g => g.calculate)
  const totalWins = calculatedGames.reduce((sum, g) => sum + (gameStats.value.find(gs => gs.game.id === g.game.id)?.matches || 0), 0)
  const totalResults = calculatedGames.reduce((sum, g) => sum + (gameStats.value.find(gs => gs.game.id === g.game.id)?.totalResults || 0), 0)
  const totalWinAmount = calculatedGames.reduce((sum, g) => sum + (gameStats.value.find(gs => gs.game.id === g.game.id)?.winAmount || 0), 0)
  const totalLossAmount = calculatedGames.reduce((sum, g) => sum + (gameStats.value.find(gs => gs.game.id === g.game.id)?.lossAmount || 0), 0)
  
  return {
    games: calculatedGames.length,
    wins: totalWins,
    losses: totalResults - totalWins,
    winAmount: totalWinAmount,
    lossAmount: totalLossAmount,
    netAmount: totalWinAmount - totalLossAmount
  }
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

const handleAddMultipleGames = (gameIds: number[]) => {
  if (!props.gameMap) return
  
  emit('gameOperationLoading', true)
  
  setTimeout(() => {
    gameIds.forEach(gameId => {
      const game = props.gameMap!.get(gameId)
      if (game) {
        selectedGames.value.push({ game, calculate: true })
      }
    })
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
  const key = `${gameId}-${date}-${targetDigits.value.join(',')}-${matchMethod.value}-${noDuplicate.value}`
  
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
        const hasTargetDigit = targetDigits.value.length > 0 && checkMatch(result.result_3up!)
        cssClass = hasTargetDigit
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
  
  setTimeout(() => {
    emit('gameOperationLoading', false)
  }, 100)
}

// Match checking function
const checkMatch = (result: string) => {
  if (targetDigits.value.length === 0) return false
  
  // Check if number has duplicates and noDuplicate is enabled
  if (noDuplicate.value && hasDuplicateDigits(result)) {
    return false
  }
  
  if (matchMethod.value === 'OR') {
    return targetDigits.value.some(digit => result.includes(digit))
  } else {
    return targetDigits.value.every(digit => result.includes(digit))
  }
}

// Flag to prevent clearing digits during profile load
const isLoadingProfile = ref(false)

// Watch for match method changes - clear digits (but not during profile load)
watch(matchMethod, () => {
  if (!isLoadingProfile.value) {
    targetDigits.value = []
  }
  cellCache.clear()
})

// Profile methods
const saveCurrentProfile = async () => {
  if (!selectedProfileId.value) return
  
  const currentProfile = profiles.value.find(p => p.id === selectedProfileId.value)
  if (!currentProfile) return
  
  const profileData = {
    profile_name: currentProfile.profile_name,
    match_method: matchMethod.value,
    target_digits: targetDigits.value,
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate })),
    bet_amount: betAmount.value,
    no_duplicate: noDuplicate.value
  }
  
  const success = await saveCurrentProfileComposable([], [], profileData, 'target_number')
  if (success) {
    // Update loaded state for TargetNumber
    updateLoadedState([], [])
    hasUnsavedChanges.value = false
  }
}

const saveAsNewProfile = async () => {
  const profileData = {
    match_method: matchMethod.value,
    target_digits: targetDigits.value,
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate })),
    bet_amount: betAmount.value,
    no_duplicate: noDuplicate.value
  }
  const success = await saveAsNewProfileComposable(newProfileName.value, [], [], profileData, 'target_number')
  if (success) {
    showSaveAsNewForm.value = false
    newProfileName.value = ''
  }
}

const deleteProfile = async () => {
  await deleteProfileComposable()
}

// Watch for profile selection changes
watch(selectedProfileId, (newProfileId) => {
  if (newProfileId) {
    loadProfile()
  } else {
    matchMethod.value = 'OR'
    targetDigits.value = []
    selectedGames.value = []
    betAmount.value = 10
    noDuplicate.value = false
    clearProfile()
  }
})

const loadProfile = async () => {
  if (!selectedProfileId.value || !props.gameMap) return
  
  const profile = profiles.value.find(p => p.id === selectedProfileId.value)
  if (!profile) return
  
  console.log('Loading profile:', profile) // Debug log
  
  // Set loading flag to prevent digit clearing
  isLoadingProfile.value = true
  
  await nextTick() // Ensure flag is set before any changes
  
  // Load TargetNumber data from game_pattern_bets field
  const targetData = (profile as any).game_pattern_bets || {}
  console.log('Target data:', targetData)
  
  targetData.bet_amount = profile.bet_amount || 10 // Default to 10 if not set

  // Load all data at once to avoid multiple watch triggers
  if (targetData.match_method) {
    matchMethod.value = targetData.match_method
    console.log('Loaded match_method:', targetData.match_method)
  }
  
  if (targetData.target_digits) {
    targetDigits.value = targetData.target_digits
    console.log('Loaded target_digits:', targetData.target_digits)
  }
  
  if (targetData.selected_games) {
    selectedGames.value = targetData.selected_games
      .map((item: any) => {
        const game = props.gameMap!.get(item.gameId)
        return game ? { game, calculate: item.calculate } : null
      })
      .filter(Boolean)
    console.log('Loaded selected_games:', selectedGames.value)
  }

  
  if (targetData.bet_amount !== undefined && targetData.bet_amount !== null) {
    betAmount.value = targetData.bet_amount
    console.log('Loaded bet_amount:', targetData.bet_amount)
  } else {
    betAmount.value = 10 // Default value
    console.log('Using default bet_amount: 10')
  }
  
  if (targetData.no_duplicate !== undefined) {
    noDuplicate.value = targetData.no_duplicate
    console.log('Loaded no_duplicate:', targetData.no_duplicate)
  } else {
    noDuplicate.value = false
    console.log('Using default no_duplicate: false')
  }
  
  // Store loaded state for TargetNumber
  loadedProfileState.value = {
    match_method: matchMethod.value,
    target_digits: [...targetDigits.value],
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate })),
    bet_amount: betAmount.value,
    no_duplicate: noDuplicate.value
  }
  hasUnsavedChanges.value = false
  
  // Clear loading flag after next tick
  await nextTick()
  isLoadingProfile.value = false
}

// Helper functions
const formatCurrency = (amount: number): string => {
  return amount.toLocaleString()
}

const getNetClass = (amount: number): string => {
  if (amount > 0) return 'text-green-600'
  if (amount < 0) return 'text-red-600'
  return 'text-gray-600'
}

const formatMonth = (month: string) => {
  const [year, monthNum] = month.split('-')
  const monthNames = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
  return `${monthNames[parseInt(monthNum) - 1]} ${year}`
}

const getWinRate = (wins: number, losses: number) => {
  const total = wins + losses
  return total > 0 ? Math.round((wins / total) * 100) : 0
}

// Track unsaved changes for TargetNumber
watch([matchMethod, targetDigits, selectedGames, betAmount, noDuplicate], () => {
  if (selectedProfileId.value && loadedProfileState.value) {
    const current = {
      match_method: matchMethod.value,
      target_digits: [...targetDigits.value],
      selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate })),
      bet_amount: betAmount.value,
      no_duplicate: noDuplicate.value
    }
    
    const loaded = loadedProfileState.value
    const hasChanges = (
      current.match_method !== loaded.match_method ||
      JSON.stringify(current.target_digits) !== JSON.stringify(loaded.target_digits) ||
      JSON.stringify(current.selected_games) !== JSON.stringify(loaded.selected_games) ||
      current.bet_amount !== loaded.bet_amount ||
      current.no_duplicate !== loaded.no_duplicate
    )
    
    hasUnsavedChanges.value = hasChanges
  }
}, { deep: true })

// Watch for target digits and settings changes and clear cache
watch([targetDigits, matchMethod, noDuplicate], () => {
  // Clear cell cache when target digits or settings change
  cellCache.clear()
}, { deep: true })

// Template ref
const previewTableContainer = ref<HTMLElement | null>(null)

// Auto-scroll to right when results load
watch(() => tableData.value.dates.length, (newLength) => {
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
  await fetchProfiles('target_number')
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