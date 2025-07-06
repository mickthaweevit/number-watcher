<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-6">รายงาน</h2>
    
    <!-- Loading Overlay -->
    <div v-if="loading || profilesLoading || profileLoading || gameOperationLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg flex items-center space-x-3">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span>{{ profileLoading ? 'กำลังโหลดโปรไฟล์...' : gameOperationLoading ? 'กำลังประมวลผล...' : 'Loading...' }}</span>
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
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">จัดการหวย</h3>
      <div class="flex gap-3 mb-4">
        <select
          v-model="selectedGameId"
          class="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">เลือกหวยที่จะเพิ่ม</option>
          <option v-for="game in availableGames" :key="game.id" :value="game.id">
            {{ game.game_name }}
          </option>
        </select>
        <button
          @click="addGame"
          :disabled="!selectedGameId"
          class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          เพิ่มหวย
        </button>
        <button
          @click="openReorderDialog"
          :disabled="selectedGames.length < 2"
          class="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          จัดเรียง
        </button>
      </div>
      
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
    </div>
    
    <!-- Pattern Highlighting Controls -->
    <div class="p-4 rounded-lg mb-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">รูปแบบที่แสดงในตาราง (เฉพาะการแสดงผล)</label>
        <div class="flex flex-wrap gap-2">
          <label v-for="pattern in availablePatterns" :key="pattern.key" class="flex items-center border border-gray-300 px-3 py-2 rounded" :class="pattern.colorClass">
            <input
              v-model="selectedPatterns"
              :value="pattern.key"
              type="checkbox"
              class="mr-2"
            />
            <span class="text-sm">{{ pattern.label }}</span>
          </label>
        </div>
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
                          <th class="px-2 py-1 text-center font-medium text-gray-600">รวม</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600">ถูก</th>
                          <th class="px-2 py-1 text-center font-medium text-gray-600">รวม</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="monthData in getMonthlyData(gameAnalysis.game.id)" :key="monthData.month" class="border-b border-gray-200">
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
    <div v-if="selectedGames.some(g => g.calculate)" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Total Statistics -->
      <div class="bg-gray-50 p-4 rounded">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">สถิติรวม</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span>หวยทั้งหมด:</span>
            <span class="font-medium">{{ totalStats.games }}</span>
          </div>
          <div class="flex justify-between">
            <span>ผลทั้งหมด:</span>
            <span class="font-medium">{{ totalStats.results }}</span>
          </div>
          <div class="flex justify-between">
            <span>รูปแบบตรง:</span>
            <span class="font-medium text-green-600">{{ totalStats.wins }}</span>
          </div>
          <div class="flex justify-between">
            <span>ไม่ตรง:</span>
            <span class="font-medium text-red-600">{{ totalStats.losses }}</span>
          </div>
          <div class="flex justify-between border-t pt-2">
            <span class="font-semibold">ผลรวม:</span>
            <span class="font-bold" :class="getNetClass(totalStats.netAmount)">
              {{ formatCurrency(totalStats.netAmount) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Monthly Statistics -->
      <div class="bg-gray-50 p-4 rounded">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">สถิติรายเดือน</h3>
        <div class="max-h-64 overflow-y-auto">
          <div v-for="month in monthlyStats" :key="month.month" class="mb-3 p-2 bg-white rounded">
            <div class="font-medium text-sm text-gray-700 mb-1">{{ month.month }}</div>
            <div class="grid grid-cols-3 gap-2 text-xs">
              <div>ทั้งหมด: <span class="font-medium">{{ month.wins + month.losses }}</span></div>
              <div>ถูก: <span class="text-green-600 font-medium">{{ month.wins }}</span></div>
              <div>ผิด: <span class="text-red-600 font-medium">{{ month.losses }}</span></div>
            </div>
            <div class="text-xs mt-1">
              รวม: <span class="font-medium" :class="getNetClass(month.netAmount)">{{ formatCurrency(month.netAmount) }}</span>
            </div>
          </div>
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

    <!-- Reorder Games Modal -->
    <div v-if="showReorderDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg max-w-2xl w-full mx-4">
        <h3 class="text-xl font-bold mb-4">จัดเรียงลำดับหวย</h3>
        <div class="max-h-96 overflow-y-auto mb-4">
          <div v-for="(game, index) in reorderGames" :key="game.game.id" class="flex items-center justify-between p-3 border border-gray-200 rounded mb-2">
            <span class="flex-1 text-base truncate">{{ game.game.game_name }}</span>
            <div class="flex gap-2">
              <button @click="moveGameUp(index)" :disabled="index === 0" class="p-2 text-blue-600 hover:text-blue-800 disabled:text-gray-400 hover:bg-blue-50 rounded">
                <svg class="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M7 14l5-5 5 5z"/>
                </svg>
              </button>
              <button @click="moveGameDown(index)" :disabled="index === reorderGames.length - 1" class="p-2 text-blue-600 hover:text-blue-800 disabled:text-gray-400 hover:bg-blue-50 rounded">
                <svg class="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <button @click="saveReorder" class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            บันทึก
          </button>
          <button @click="cancelReorder" class="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
            ยกเลิก
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { gameApi, authApi, profileApi } from '../services/api'
import type { Game, Result, User, DashboardProfile } from '../types'

// Reactive state
const betAmount = ref(10) // Default bet amount
const selectedPatterns = ref<string[]>([])
const selectedGameId = ref('')
const selectedGames = ref<GameAnalysis[]>([])
const allGames = ref<Game[]>([])
const allResults = ref<Result[]>([])
const loading = ref(false)
const profilesLoading = ref(false)
const gameOperationLoading = ref(false)
const profileLoading = ref(false)

// Expandable rows state
const expandedRows = ref<Set<number>>(new Set())

// Reorder dialog state
const showReorderDialog = ref(false)
const reorderGames = ref<GameAnalysis[]>([])

// Cached maps for performance
let gameMap: Map<number, Game> | null = null
let resultsByGame: Map<number, Result[]> | null = null
let validResultsByGame: Map<number, Result[]> | null = null // Pre-filtered valid results
let analysisCache: Map<string, GameAnalysis> = new Map()

// User state (always logged in now)
const user = ref<User | null>(null)

// Profile state
const profiles = ref<DashboardProfile[]>([])
const selectedProfileId = ref<number | null>(null)
const showSaveProfileForm = ref(false)
const showSaveAsNewForm = ref(false)
const newProfileName = ref('')
const loadedProfileState = ref<any>(null)
const hasUnsavedChanges = ref(false)

// Request cancellation
let loadProfileAbortController: AbortController | null = null

// Pattern definitions with count information
const availablePatterns = [
  // { key: 'all_same', label: 'All Same:ตอง (111, 222, 333...) - 10 numbers', count: 10 },
  { key: 'first_two', label: 'เบิ้ลหน้า', colorClass: 'bg-blue-100', count: 90 },
  { key: 'first_third', label: 'หาม', colorClass: 'bg-green-100', count: 90 },
  { key: 'last_two', label: 'เบิ้ลหลัง', colorClass: 'bg-yellow-100', count: 90 }
]

interface PatternAnalysis {
  betAmount: number
  wins: number
  losses: number
  winAmount: number
  lossAmount: number
  netAmount: number
  monthlyBreakdown: { [month: string]: { wins: number, losses: number, netAmount: number } }
}

interface GameAnalysis {
  game: Game
  calculate: boolean
  totalResults: number
  patterns: {
    first_two: PatternAnalysis
    first_third: PatternAnalysis
    last_two: PatternAnalysis
  }
  // Legacy fields for compatibility
  patternMatches: number
  winAmount: number
  lossAmount: number
  netAmount: number
  monthlyBreakdown: { [month: string]: { wins: number, losses: number, netAmount: number } }
}

// Computed properties
const availableGames = computed(() => {
  return allGames.value.filter(game => 
    !selectedGames.value.some(sg => sg.game.id === game.id)
  )
})

const canSaveCurrent = computed(() => {
  return selectedProfileId.value !== null && hasUnsavedChanges.value
})

const totalStats = computed(() => {
  const calculatedGames = selectedGames.value.filter(g => g.calculate)
  return {
    games: calculatedGames.length,
    results: calculatedGames.reduce((sum, g) => sum + g.totalResults, 0),
    wins: calculatedGames.reduce((sum, g) => sum + g.patternMatches, 0),
    losses: calculatedGames.reduce((sum, g) => sum + (g.totalResults - g.patternMatches), 0),
    netAmount: calculatedGames.reduce((sum, g) => sum + g.netAmount, 0)
  }
})

const monthlyStats = computed(() => {
  const monthlyData: { [month: string]: { wins: number, losses: number, netAmount: number } } = {}
  
  selectedGames.value.filter(g => g.calculate).forEach(game => {
    Object.entries(game.monthlyBreakdown).forEach(([month, data]) => {
      if (!monthlyData[month]) {
        monthlyData[month] = { wins: 0, losses: 0, netAmount: 0 }
      }
      monthlyData[month].wins += data.wins
      monthlyData[month].losses += data.losses
      monthlyData[month].netAmount += data.netAmount
    })
  })
  
  return Object.entries(monthlyData)
    .map(([month, data]) => ({ month, ...data }))
    .sort((a, b) => a.month.localeCompare(b.month))
})

// Methods
const fetchData = async () => {
  try {
    loading.value = true
    const [games, results] = await Promise.all([
      gameApi.getAllGames(),
      gameApi.getAllResults()
    ])
    allGames.value = games
    allResults.value = results
    
    // Pre-compute maps once for O(1) lookups
    gameMap = new Map(games.map(g => [g.id, g]))
    resultsByGame = new Map()
    validResultsByGame = new Map()
    
    results.forEach(r => {
      if (r.result_3up) {
        if (!resultsByGame.has(r.game_id)) {
          resultsByGame.set(r.game_id, [])
        }
        resultsByGame.get(r.game_id).push(r)
        
        // Pre-filter valid results for analysis
        if (r.status === 'completed') {
          if (!validResultsByGame.has(r.game_id)) {
            validResultsByGame.set(r.game_id, [])
          }
          validResultsByGame.get(r.game_id).push(r)
        }
      }
    })
    
    // Clear analysis cache when data changes
    analysisCache.clear()
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const addGame = () => {
  if (!gameMap || !validResultsByGame) return
  
  const gameId = parseInt(selectedGameId.value)
  const game = gameMap.get(gameId)
  if (!game) return
  
  gameOperationLoading.value = true
  
  setTimeout(() => {
    const gameResults = validResultsByGame.get(gameId) || []
    const analysis = analyzeGameOptimized(game, gameResults)
    
    selectedGames.value.push(analysis)
    selectedGameId.value = ''
    gameOperationLoading.value = false
  }, 0)
}

const removeGame = (gameId: number) => {
  gameOperationLoading.value = true
  
  setTimeout(() => {
    selectedGames.value = selectedGames.value.filter(g => g.game.id !== gameId)
    gameOperationLoading.value = false
  }, 0)
}

const analyzeGameOptimized = (game: Game, results: Result[]): GameAnalysis => {
  const totalResults = results.length
  
  // Initialize pattern analysis
  const patterns = {
    first_two: createEmptyPatternAnalysis(),
    first_third: createEmptyPatternAnalysis(), 
    last_two: createEmptyPatternAnalysis()
  }
  
  // Analyze each result for all patterns
  for (const result of results) {
    if (!result.result_3up || result.result_3up.length !== 3) continue
    
    const [d1, d2, d3] = result.result_3up.split('')
    const month = result.result_date.slice(0, 7)
    
    // Check each pattern
    if (d1 === d2 && d2 !== d3) {
      updatePatternAnalysis(patterns.first_two, month, true)
    } else {
      updatePatternAnalysis(patterns.first_two, month, false)
    }
    
    if (d1 === d3 && d1 !== d2) {
      updatePatternAnalysis(patterns.first_third, month, true)
    } else {
      updatePatternAnalysis(patterns.first_third, month, false)
    }
    
    if (d2 === d3 && d1 !== d2) {
      updatePatternAnalysis(patterns.last_two, month, true)
    } else {
      updatePatternAnalysis(patterns.last_two, month, false)
    }
  }
  
  return {
    game,
    calculate: true,
    totalResults,
    patterns,
    // Legacy fields for compatibility
    patternMatches: 0,
    winAmount: 0,
    lossAmount: 0,
    netAmount: 0,
    monthlyBreakdown: {}
  }
}

const createEmptyPatternAnalysis = (): PatternAnalysis => ({
  betAmount: 0,
  wins: 0,
  losses: 0,
  winAmount: 0,
  lossAmount: 0,
  netAmount: 0,
  monthlyBreakdown: {}
})

const updatePatternAnalysis = (pattern: PatternAnalysis, month: string, isWin: boolean) => {
  if (!pattern.monthlyBreakdown[month]) {
    pattern.monthlyBreakdown[month] = { wins: 0, losses: 0, netAmount: 0 }
  }
  
  if (isWin) {
    pattern.wins++
    pattern.monthlyBreakdown[month].wins++
  } else {
    pattern.losses++
    pattern.monthlyBreakdown[month].losses++
  }
}

const recalculateGame = (gameAnalysis: GameAnalysis) => {
  // Recalculate financial data for each pattern
  Object.values(gameAnalysis.patterns).forEach(pattern => {
    const dailyBetAmount = 90 * pattern.betAmount // 90 numbers per pattern
    pattern.winAmount = pattern.wins * pattern.betAmount * 1000
    pattern.lossAmount = gameAnalysis.totalResults * dailyBetAmount
    pattern.netAmount = pattern.winAmount - pattern.lossAmount
    
    // Update monthly breakdown
    Object.values(pattern.monthlyBreakdown).forEach(monthData => {
      monthData.netAmount = (monthData.wins * pattern.betAmount * 1000) - ((monthData.wins + monthData.losses) * dailyBetAmount)
    })
  })
}

const getTotalWins = (gameAnalysis: GameAnalysis): number => {
  return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
    return sum + (pattern.betAmount > 0 ? pattern.wins : 0)
  }, 0)
}

const getTotalWinAmount = (gameAnalysis: GameAnalysis): number => {
  return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
    return sum + (pattern.betAmount > 0 ? pattern.winAmount : 0)
  }, 0)
}

const getTotalLossAmount = (gameAnalysis: GameAnalysis): number => {
  return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
    return sum + (pattern.betAmount > 0 ? pattern.lossAmount : 0)
  }, 0)
}

const getTotalNetAmount = (gameAnalysis: GameAnalysis): number => {
  return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
    return sum + (pattern.betAmount > 0 ? pattern.netAmount : 0)
  }, 0)
}

const analyzeGame = (game: Game, results: Result[]): GameAnalysis => {
  let patternMatches = 0
  const monthlyBreakdown: { [month: string]: { wins: number, losses: number, netAmount: number } } = {}
  
  // Calculate total numbers to bet per day based on selected patterns
  const getTotalBetNumbers = () => {
    return selectedPatterns.value.reduce((total, pattern) => {
      const patternInfo = availablePatterns.find(p => p.key === pattern)
      return total + (patternInfo?.count || 0)
    }, 0)
  }
  
  const totalBetNumbers = getTotalBetNumbers()
  const dailyBetAmount = totalBetNumbers * betAmount.value // e.g., 90 * 10 = 900 per day
  
  results.forEach(result => {
    if (!result.result_3up || result.status !== 'completed') return
    
    const isMatch = checkPatternMatch(result.result_3up)
    const month = new Date(result.result_date).toISOString().slice(0, 7) // YYYY-MM
    
    if (!monthlyBreakdown[month]) {
      monthlyBreakdown[month] = { wins: 0, losses: 0, netAmount: 0 }
    }
    
    if (isMatch) {
      patternMatches++
      monthlyBreakdown[month].wins++
      // Win: get bet amount * 1000, but still pay daily bet amount
      monthlyBreakdown[month].netAmount += (betAmount.value * 1000) - dailyBetAmount
    } else {
      monthlyBreakdown[month].losses++
      // Lose: lose the daily bet amount (all numbers bet that day)
      monthlyBreakdown[month].netAmount -= dailyBetAmount
    }
  })
  
  const totalResults = results.filter(r => r.result_3up && r.status === 'completed').length
  const winAmount = patternMatches * betAmount.value * 1000 // Prize per win
  const totalBetAmount = totalResults * dailyBetAmount // Total amount bet across all days
  const lossAmount = totalBetAmount // Amount lost
  const netAmount = winAmount - totalBetAmount // Net = total winnings - total bets
  
  return {
    game,
    calculate: true,
    totalResults,
    patternMatches,
    winAmount,
    lossAmount: Math.max(0, lossAmount), // Don't show negative loss
    netAmount,
    monthlyBreakdown
  }
}

const checkPatternMatch = (result: string): boolean => {
  if (result.length !== 3) return false
  
  const [d1, d2, d3] = result.split('')
  
  return selectedPatterns.value.some(pattern => {
    switch (pattern) {
      case 'all_same':
        return d1 === d2 && d2 === d3
      case 'first_two':
        return d1 === d2 && d2 !== d3
      case 'first_third':
        return d1 === d3 && d1 !== d2
      case 'last_two':
        return d2 === d3 && d1 !== d2
      default:
        return false
    }
  })
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

// Watch for changes in global settings
const recalculateAllGames = () => {
  if (!resultsByGame) return
  
  gameOperationLoading.value = true
  
  setTimeout(() => {
    selectedGames.value.forEach(gameAnalysis => {
      if (gameAnalysis.calculate) {
        const gameResults = resultsByGame.get(gameAnalysis.game.id) || []
        const newAnalysis = analyzeGame(gameAnalysis.game, gameResults)
        Object.assign(gameAnalysis, newAnalysis)
      }
    })
    gameOperationLoading.value = false
  }, 0)
}

// Helper function to check for unsaved changes
const checkForUnsavedChanges = () => {
  if (!loadedProfileState.value) return false
  
  const arraysEqual = (a: any[], b: any[]) => {
    return a.length === b.length && a.every((val, i) => val === b[i])
  }
  
  // Check if game pattern bets changed
  const currentGameBets = selectedGames.value.reduce((acc, game) => {
    acc[game.game.id] = {
      first_two: game.patterns.first_two.betAmount,
      first_third: game.patterns.first_third.betAmount,
      last_two: game.patterns.last_two.betAmount
    }
    return acc
  }, {} as Record<number, any>)
  
  const savedGameBets = loadedProfileState.value.gamePatternBets || {}
  const gameBetsChanged = JSON.stringify(currentGameBets) !== JSON.stringify(savedGameBets)
  
  return (
    !arraysEqual(selectedPatterns.value, loadedProfileState.value.selectedPatterns) ||
    !arraysEqual(selectedGames.value.map(g => g.game.id), loadedProfileState.value.selectedGameIds) ||
    gameBetsChanged
  )
}

// Watch for profile selection changes - auto load
watch(selectedProfileId, (newProfileId) => {
  if (newProfileId) {
    loadProfile()
  } else {
    // Clear everything when no profile selected
    selectedGames.value = []
    betAmount.value = 10
    selectedPatterns.value = []
    loadedProfileState.value = null
    hasUnsavedChanges.value = false
  }
})

// Watch for changes in bet amount or patterns with debouncing
watch([betAmount, selectedPatterns], () => {
  analysisCache.clear() // Clear cache when settings change
  recalculateAllGames()
}, { deep: true })

// Track unsaved changes
watch([betAmount, selectedPatterns, selectedGames], () => {
  if (selectedProfileId.value && loadedProfileState.value) {
    hasUnsavedChanges.value = checkForUnsavedChanges()
  }
}, { deep: true })

// Get current user (always authenticated)
const getCurrentUser = async () => {
  try {
    user.value = await authApi.getCurrentUser()
    await fetchProfiles()
  } catch (error) {
    console.error('Failed to get user:', error)
  }
}

// Profile methods
const fetchProfiles = async () => {
  profilesLoading.value = true
  try {
    profiles.value = await profileApi.getProfiles()
  } catch (error) {
    console.error('Failed to fetch profiles:', error)
  } finally {
    profilesLoading.value = false
  }
}

const saveCurrentProfile = async () => {
  if (!selectedProfileId.value) return
  
  try {
    const profileData = {
      profile_name: profiles.value.find(p => p.id === selectedProfileId.value)?.profile_name || '',
      bet_amount: 0, // Legacy field, not used anymore
      selected_patterns: selectedPatterns.value,
      selected_game_ids: selectedGames.value.map(g => g.game.id),
      game_pattern_bets: selectedGames.value.reduce((acc, game) => {
        acc[game.game.id] = {
          first_two: game.patterns.first_two.betAmount,
          first_third: game.patterns.first_third.betAmount,
          last_two: game.patterns.last_two.betAmount
        }
        return acc
      }, {} as Record<number, any>)
    }
    
    await profileApi.updateProfile(selectedProfileId.value, profileData)
    await fetchProfiles()
    
    // Update loaded state
    loadedProfileState.value = {
      selectedPatterns: [...selectedPatterns.value],
      selectedGameIds: [...selectedGames.value.map(g => g.game.id)],
      gamePatternBets: selectedGames.value.reduce((acc, game) => {
        acc[game.game.id] = {
          first_two: game.patterns.first_two.betAmount,
          first_third: game.patterns.first_third.betAmount,
          last_two: game.patterns.last_two.betAmount
        }
        return acc
      }, {} as Record<number, any>)
    }
    
    hasUnsavedChanges.value = false
    alert('บันทึกโปรไฟล์สำเร็จแล้ว!')
  } catch (error) {
    alert('บันทึกโปรไฟล์ล้มเหลว')
  }
}

const saveAsNewProfile = async () => {
  if (!newProfileName.value.trim()) {
    alert('กรุณากรอกชื่อโปรไฟล์')
    return
  }
  
  try {
    const profileData = {
      profile_name: newProfileName.value,
      bet_amount: 0, // Legacy field, not used anymore
      selected_patterns: selectedPatterns.value,
      selected_game_ids: selectedGames.value.map(g => g.game.id),
      game_pattern_bets: selectedGames.value.reduce((acc, game) => {
        acc[game.game.id] = {
          first_two: game.patterns.first_two.betAmount,
          first_third: game.patterns.first_third.betAmount,
          last_two: game.patterns.last_two.betAmount
        }
        return acc
      }, {} as Record<number, any>)
    }
    
    await profileApi.createProfile(profileData)
    await fetchProfiles()
    showSaveAsNewForm.value = false
    newProfileName.value = ''
    alert('สร้างโปรไฟล์ใหม่สำเร็จแล้ว!')
  } catch (error) {
    alert('สร้างโปรไฟล์ล้มเหลว ชื่ออาจถูกใช้แล้ว')
  }
}

const loadProfile = async () => {
  if (!selectedProfileId.value || !gameMap || !validResultsByGame) return
  
  // Cancel previous request
  if (loadProfileAbortController) {
    loadProfileAbortController.abort()
  }
  loadProfileAbortController = new AbortController()
  
  profileLoading.value = true
  
  try {
    const profile = profiles.value.find(p => p.id === selectedProfileId.value)
    if (!profile || loadProfileAbortController.signal.aborted) return
    
    // Apply settings immediately
    selectedPatterns.value = [...profile.selected_patterns]
    
    // Use setTimeout to allow UI to update with loading state
    await new Promise(resolve => setTimeout(resolve, 0))
    
    // Batch load games using cached maps and pre-filtered results
    selectedGames.value = profile.selected_game_ids
      .map(gameId => {
        const game = gameMap.get(gameId)
        if (!game) return null
        
        const analysis = analyzeGameOptimized(game, validResultsByGame.get(gameId) || [])
        
        // Restore per-game pattern bet amounts
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
    
    // Store state
    loadedProfileState.value = {
      selectedPatterns: [...profile.selected_patterns],
      selectedGameIds: [...profile.selected_game_ids],
      gamePatternBets: (profile as any).game_pattern_bets || {}
    }
    
    hasUnsavedChanges.value = false
    
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('Profile load error:', error)
    }
  } finally {
    profileLoading.value = false
    loadProfileAbortController = null
  }
}

const deleteProfile = async () => {
  if (!selectedProfileId.value) return
  
  const profile = profiles.value.find(p => p.id === selectedProfileId.value)
  if (!profile) return
  
  if (confirm(`Delete profile "${profile.profile_name}"?`)) {
    try {
      await profileApi.deleteProfile(selectedProfileId.value)
      await fetchProfiles()
      selectedProfileId.value = null
      alert('Profile deleted successfully!')
    } catch (error) {
      alert('Failed to delete profile')
    }
  }
}

// Base table data (doesn't change with patterns)
const baseTableData = computed(() => {
  if (selectedGames.value.length === 0) return { dates: [], games: [], cells: {} }
  
  const gameIds = selectedGames.value.map(g => g.game.id)
  const resultDates = Array.from(new Set(
    allResults.value
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
      const result = allResults.value.find(r => r.game_id === gameAnalysis.game.id && r.result_date === date)
      
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

const getMonthlyData = (gameId: number) => {
  const game = selectedGames.value.find(g => g.game.id === gameId)
  if (!game) return []
  
  // Get months only from patterns with betAmount > 0
  const allMonths = new Set<string>()
  Object.values(game.patterns).forEach(pattern => {
    if (pattern.betAmount > 0) {
      Object.keys(pattern.monthlyBreakdown).forEach(month => allMonths.add(month))
    }
  })
  
  return Array.from(allMonths).map(month => {
    const firstTwo = game.patterns.first_two.betAmount > 0 ? {
      wins: game.patterns.first_two.monthlyBreakdown[month]?.wins || 0,
      losses: game.patterns.first_two.monthlyBreakdown[month]?.losses || 0
    } : { wins: 0, losses: 0 }
    
    const firstThird = game.patterns.first_third.betAmount > 0 ? {
      wins: game.patterns.first_third.monthlyBreakdown[month]?.wins || 0,
      losses: game.patterns.first_third.monthlyBreakdown[month]?.losses || 0
    } : { wins: 0, losses: 0 }
    
    const lastTwo = game.patterns.last_two.betAmount > 0 ? {
      wins: game.patterns.last_two.monthlyBreakdown[month]?.wins || 0,
      losses: game.patterns.last_two.monthlyBreakdown[month]?.losses || 0
    } : { wins: 0, losses: 0 }
    
    let netAmount = 0
    if (game.patterns.first_two.betAmount > 0) netAmount += game.patterns.first_two.monthlyBreakdown[month]?.netAmount || 0
    if (game.patterns.first_third.betAmount > 0) netAmount += game.patterns.first_third.monthlyBreakdown[month]?.netAmount || 0
    if (game.patterns.last_two.betAmount > 0) netAmount += game.patterns.last_two.monthlyBreakdown[month]?.netAmount || 0
    
    return {
      month,
      firstTwo,
      firstThird, 
      lastTwo,
      allWins: firstTwo.wins + firstThird.wins + lastTwo.wins,
      allLosses: firstTwo.losses + firstThird.losses + lastTwo.losses,
      netAmount
    }
  }).sort((a, b) => a.month.localeCompare(b.month))
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

// Reorder dialog methods
const openReorderDialog = () => {
  reorderGames.value = [...selectedGames.value]
  showReorderDialog.value = true
}

const moveGameUp = (index: number) => {
  if (index > 0) {
    const game = reorderGames.value[index]
    reorderGames.value.splice(index, 1)
    reorderGames.value.splice(index - 1, 0, game)
  }
}

const moveGameDown = (index: number) => {
  if (index < reorderGames.value.length - 1) {
    const game = reorderGames.value[index]
    reorderGames.value.splice(index, 1)
    reorderGames.value.splice(index + 1, 0, game)
  }
}

const saveReorder = () => {
  gameOperationLoading.value = true
  
  setTimeout(() => {
    selectedGames.value = [...reorderGames.value]
    showReorderDialog.value = false
    gameOperationLoading.value = false
  }, 0)
}

const cancelReorder = () => {
  showReorderDialog.value = false
  reorderGames.value = []
}

// Navigation guards and lifecycle
// 1. Vue Router guard (catches internal navigation)
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    if (confirm('คุณมีการเปลี่ยนแปลงที่ยังไม่ได้บันทึก ต้องการออกจากหน้านี้?')) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})

// Lifecycle
onMounted(async () => {
  await getCurrentUser()
  await fetchData()
  
  // 2. Browser beforeunload (catches external navigation)
  const handleBeforeUnload = (e: BeforeUnloadEvent) => {
    if (hasUnsavedChanges.value) {
      e.preventDefault()
      e.returnValue = '' // Required for Chrome
    }
  }
  
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // Cleanup on unmount
  onUnmounted(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })
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