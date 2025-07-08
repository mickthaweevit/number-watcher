<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-6">รายงาน</h2>
    
    <!-- Tab Navigation -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'nhl'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'nhl'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          หน้า-หาม-หลัง
        </button>
        <button
          @click="activeTab = 'new'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'new'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          ปั้กเป้า
        </button>
      </nav>
    </div>
    
    <!-- Tab Content -->
    <div v-if="activeTab === 'nhl'">
      <NHLDashboard 
        :allGames="allGames"
        :allResults="allResults"
        :gameMap="gameMap"
        :validResultsByGame="validResultsByGame"
        :gameOperationLoading="gameOperationLoading"
        @gameOperationLoading="gameOperationLoading = $event"
      />
    </div>
    
    <!-- New Dashboard Tab -->
    <div v-else-if="activeTab === 'new'">
      <TargetNumber 
        :allGames="allGames"
        :allResults="allResults"
        :gameMap="gameMap"
        :validResultsByGame="validResultsByGame"
        :gameOperationLoading="gameOperationLoading"
        @gameOperationLoading="gameOperationLoading = $event"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { gameApi } from '../services/api'
import type { Game, Result } from '../types'
import NHLDashboard from '../components/NHLDashboard.vue'
import TargetNumber from '../components/TargetNumber.vue'

// Reactive state
const activeTab = ref('nhl') // Default to main dashboard
const allGames = ref<Game[]>([])
const allResults = ref<Result[]>([])
const loading = ref(false)
const gameOperationLoading = ref(false)

// Cached maps for performance
let gameMap: Map<number, Game> | null = null
let validResultsByGame: Map<number, Result[]> | null = null

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
    validResultsByGame = new Map()
    
    results.forEach(r => {
      if (r.result_3up && r.status === 'completed') {
        if (!validResultsByGame.has(r.game_id)) {
          validResultsByGame.set(r.game_id, [])
        }
        validResultsByGame.get(r.game_id).push(r)
      }
    })
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await fetchData()
})
</script>