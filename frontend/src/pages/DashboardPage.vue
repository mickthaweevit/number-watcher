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
import { ref, shallowRef, onMounted } from 'vue'
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

// Reactive maps for performance — shallowRef so Vue tracks reassignment
const gameMap = shallowRef<Map<number, Game>>(new Map())
const validResultsByGame = shallowRef<Map<number, Result[]>>(new Map())

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
    gameMap.value = new Map(games.map(g => [g.id, g]))
    const tempMap = new Map<number, Result[]>()
    
    results.forEach(r => {
      if (r.result_3up && r.status === 'completed') {
        if (!tempMap.has(r.game_id)) {
          tempMap.set(r.game_id, [])
        }
        tempMap.get(r.game_id)!.push(r)
      }
    })
    validResultsByGame.value = tempMap
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