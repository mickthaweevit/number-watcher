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
        <div class="flex gap-4">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input v-model="matchMethod" value="OR" type="radio" class="rounded">
            <span>OR (มีเลขใดเลขหนึ่ง)</span>
          </label>
          <label class="flex items-center space-x-2 cursor-pointer">
            <input v-model="matchMethod" value="AND" type="radio" class="rounded">
            <span>AND (มีเลขทุกตัว สูงสุด 3 ตัว)</span>
          </label>
        </div>
      </div>
      
      <!-- Digit Selection -->
      <div class="grid grid-cols-5 gap-3">
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
    </div>
    
    <!-- Game Management -->
    <GameManager 
      :availableGames="availableGames" 
      :selectedGames="selectedGames"
      @addGame="handleAddGame"
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

// Profile UI state
const showSaveAsNewForm = ref(false)
const newProfileName = ref('')

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
  checkForUnsavedChanges,
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

// Match counting
const matchCount = computed(() => {
  if (targetDigits.value.length === 0 || selectedGames.value.length === 0) return 0
  
  const gameIds = selectedGames.value.map(g => g.game.id)
  return props.allResults
    .filter(r => gameIds.includes(r.game_id) && r.result_3up && r.status === 'completed')
    .filter(r => checkMatch(r.result_3up!))
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
    
    const matches = targetDigits.value.length > 0
      ? gameResults.filter(r => checkMatch(r.result_3up!)).length
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
  const key = `${gameId}-${date}-${targetDigits.value.join(',')}`
  
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
  
  if (matchMethod.value === 'OR') {
    return targetDigits.value.some(digit => result.includes(digit))
  } else {
    return targetDigits.value.every(digit => result.includes(digit))
  }
}

// Watch for match method changes - clear digits
watch(matchMethod, () => {
  targetDigits.value = []
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
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate }))
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
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate }))
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
    clearProfile()
  }
})

const loadProfile = async () => {
  if (!selectedProfileId.value || !props.gameMap) return
  
  const profile = profiles.value.find(p => p.id === selectedProfileId.value)
  if (!profile) return
  
  console.log('Loading profile:', profile) // Debug log
  
  // Reset to defaults first
  matchMethod.value = 'OR'
  targetDigits.value = []
  selectedGames.value = []
  
  // Load TargetNumber data from game_pattern_bets field
  const targetData = (profile as any).game_pattern_bets || {}
  console.log('Target data:', targetData)
  
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
  
  // Store loaded state for TargetNumber
  loadedProfileState.value = {
    match_method: matchMethod.value,
    target_digits: [...targetDigits.value],
    selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate }))
  }
  hasUnsavedChanges.value = false
}

// Track unsaved changes for TargetNumber
watch([matchMethod, targetDigits, selectedGames], () => {
  if (selectedProfileId.value && loadedProfileState.value) {
    const current = {
      match_method: matchMethod.value,
      target_digits: [...targetDigits.value],
      selected_games: selectedGames.value.map(g => ({ gameId: g.game.id, calculate: g.calculate }))
    }
    
    const loaded = loadedProfileState.value
    const hasChanges = (
      current.match_method !== loaded.match_method ||
      JSON.stringify(current.target_digits) !== JSON.stringify(loaded.target_digits) ||
      JSON.stringify(current.selected_games) !== JSON.stringify(loaded.selected_games)
    )
    
    hasUnsavedChanges.value = hasChanges
  }
}, { deep: true })

// Watch for target digits changes and clear cache
watch(targetDigits, () => {
  // Clear cell cache when target digits change
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