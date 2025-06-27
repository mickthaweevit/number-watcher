<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-bold text-gray-800 mb-6">3-Up Pattern Analysis Dashboard</h2>
    
    <!-- Input Controls -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <!-- Bet Amount -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Bet Amount</label>
        <input
          v-model.number="betAmount"
          type="number"
          min="1"
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter bet amount"
        />
      </div>
      
      <!-- Pattern Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Selected Patterns</label>
        <div class="space-y-2">
          <label v-for="pattern in availablePatterns" :key="pattern.key" class="flex items-center">
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
      
      <!-- Game Selection -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Add Game</label>
        <select
          v-model="selectedGameId"
          class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
        >
          <option value="">Select a game to add</option>
          <option v-for="game in availableGames" :key="game.id" :value="game.id">
            {{ game.game_name }} ({{ game.category }})
          </option>
        </select>
        <button
          @click="addGame"
          :disabled="!selectedGameId"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Add Game
        </button>
      </div>
    </div>
    
    <!-- Selected Games Table -->
    <div v-if="selectedGames.length > 0" class="mb-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-3">Selected Games Analysis</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Calculate</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Game</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total Results</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Pattern Matches</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Win Amount</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Loss Amount</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Net</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="gameAnalysis in selectedGames" :key="gameAnalysis.game.id" class="hover:bg-gray-50">
              <td class="px-3 py-2">
                <input
                  v-model="gameAnalysis.calculate"
                  type="checkbox"
                  class="rounded"
                />
              </td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ gameAnalysis.game.game_name }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">{{ gameAnalysis.game.category }}</td>
              <td class="px-3 py-2 text-sm text-gray-600">
                {{ gameAnalysis.calculate ? gameAnalysis.totalResults : '-' }}
              </td>
              <td class="px-3 py-2 text-sm">
                <span v-if="gameAnalysis.calculate" :class="getMatchClass(gameAnalysis.patternMatches)">
                  {{ gameAnalysis.patternMatches }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="px-3 py-2 text-sm text-green-600 font-medium">
                {{ gameAnalysis.calculate ? formatCurrency(gameAnalysis.winAmount) : '-' }}
              </td>
              <td class="px-3 py-2 text-sm text-red-600 font-medium">
                {{ gameAnalysis.calculate ? formatCurrency(gameAnalysis.lossAmount) : '-' }}
              </td>
              <td class="px-3 py-2 text-sm font-medium" :class="getNetClass(gameAnalysis.netAmount)">
                {{ gameAnalysis.calculate ? formatCurrency(gameAnalysis.netAmount) : '-' }}
              </td>
              <td class="px-3 py-2">
                <button
                  @click="removeGame(gameAnalysis.game.id)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Statistics Summary -->
    <div v-if="selectedGames.some(g => g.calculate)" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Total Statistics -->
      <div class="bg-gray-50 p-4 rounded">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">Total Statistics</h3>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span>Total Games:</span>
            <span class="font-medium">{{ totalStats.games }}</span>
          </div>
          <div class="flex justify-between">
            <span>Total Results:</span>
            <span class="font-medium">{{ totalStats.results }}</span>
          </div>
          <div class="flex justify-between">
            <span>Pattern Matches:</span>
            <span class="font-medium text-green-600">{{ totalStats.wins }}</span>
          </div>
          <div class="flex justify-between">
            <span>No Matches:</span>
            <span class="font-medium text-red-600">{{ totalStats.losses }}</span>
          </div>
          <div class="flex justify-between border-t pt-2">
            <span class="font-semibold">Net Amount:</span>
            <span class="font-bold" :class="getNetClass(totalStats.netAmount)">
              {{ formatCurrency(totalStats.netAmount) }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Monthly Statistics -->
      <div class="bg-gray-50 p-4 rounded">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">Monthly Breakdown</h3>
        <div class="max-h-64 overflow-y-auto">
          <div v-for="month in monthlyStats" :key="month.month" class="mb-3 p-2 bg-white rounded">
            <div class="font-medium text-sm text-gray-700 mb-1">{{ month.month }}</div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div>Wins: <span class="text-green-600 font-medium">{{ month.wins }}</span></div>
              <div>Losses: <span class="text-red-600 font-medium">{{ month.losses }}</span></div>
            </div>
            <div class="text-xs mt-1">
              Net: <span class="font-medium" :class="getNetClass(month.netAmount)">{{ formatCurrency(month.netAmount) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { gameApi } from '../services/api'
import type { Game, Result } from '../types'

// Reactive state
const betAmount = ref(10)
const selectedPatterns = ref<string[]>([])
const selectedGameId = ref('')
const selectedGames = ref<GameAnalysis[]>([])
const allGames = ref<Game[]>([])
const allResults = ref<Result[]>([])
const loading = ref(false)

// Pattern definitions with count information
const availablePatterns = [
  { key: 'all_same', label: 'All Same:ตอง (111, 222, 333...) - 10 numbers', count: 10 },
  { key: 'first_two', label: 'First 2 Same:หน้า (113, 225, 882...) - 90 numbers', count: 90 },
  { key: 'first_third', label: 'First & Last Same:หาม (040, 747, 202...) - 90 numbers', count: 90 },
  { key: 'last_two', label: 'Last 2 Same:หลัง (200, 877, 399...) - 90 numbers', count: 90 }
]

interface GameAnalysis {
  game: Game
  calculate: boolean
  totalResults: number
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
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const addGame = () => {
  const game = allGames.value.find(g => g.id === parseInt(selectedGameId.value))
  if (!game) return
  
  const gameResults = allResults.value.filter(r => r.game_id === game.id && r.result_3up)
  const analysis = analyzeGame(game, gameResults)
  
  selectedGames.value.push(analysis)
  selectedGameId.value = ''
}

const removeGame = (gameId: number) => {
  selectedGames.value = selectedGames.value.filter(g => g.game.id !== gameId)
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
  const lossAmount = totalBetAmount - (patternMatches * betAmount.value * 1000) // Amount lost
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

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>