<template>
  <div class="mb-6 flex justify-between">
    <h3 class="text-lg font-semibold text-gray-800 mb-3">จัดการหวย</h3>
    <div class="flex gap-3">
      <button
        @click="showBulkAddDialog = true"
        :disabled="availableGames.length === 0"
        class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        เพิ่มหวย
      </button>
      <button
        @click="handleOpenReorder"
        :disabled="selectedGames.length < 2"
        class="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        จัดเรียง
      </button>
    </div>
    
    <!-- Bulk Add Games Modal -->
    <div v-if="showBulkAddDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold">เลือกหวยที่จะเพิ่ม</h3>
          <button @click="showBulkAddDialog = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
            </svg>
          </button>
        </div>
        <div class="mb-4">
          <input 
            v-model="searchFilter" 
            type="text" 
            placeholder="ค้นหาชื่อหวย..."
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>
        <div class="overflow-y-auto max-h-[60vh] mb-4">
          <table class="min-w-full bg-white border border-gray-200 rounded">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-12">
                  <input 
                    type="checkbox" 
                    @change="toggleSelectAll" 
                    :checked="selectedGameIds.length === filteredGames.length && filteredGames.length > 0"
                    class="rounded"
                  >
                </th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ชื่อหวย</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="game in filteredGames" :key="game.id" class="hover:bg-gray-100">
                <td class="px-3 py-2">
                  <input 
                    v-model="selectedGameIds" 
                    :value="game.id" 
                    type="checkbox" 
                    class="rounded"
                  >
                </td>
                <td class="px-3 py-2 text-sm text-gray-900">{{ game.game_name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex gap-3">
          <button 
            @click="handleBulkAddGames" 
            :disabled="selectedGameIds.length === 0"
            class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
          >
            เพิ่มหวย ({{ selectedGameIds.length }})
          </button>
          <button @click="showBulkAddDialog = false" class="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
            ยกเลิก
          </button>
        </div>
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
          <button @click="handleSaveReorder" class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
            บันทึก
          </button>
          <button @click="handleCancelReorder" class="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
            ยกเลิก
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Game } from '../types'
import type { GameAnalysis } from '../composables/useGameAnalysis'

interface Props {
  availableGames: Game[]
  selectedGames: GameAnalysis[]
}

interface Emits {
  (e: 'addGame', gameId: number): void
  (e: 'addMultipleGames', gameIds: number[]): void
  (e: 'reorderGames', games: GameAnalysis[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showBulkAddDialog = ref(false)
const selectedGameIds = ref<number[]>([])
const searchFilter = ref('')
const showReorderDialog = ref(false)
const reorderGames = ref<GameAnalysis[]>([])

const handleBulkAddGames = () => {
  emit('addMultipleGames', [...selectedGameIds.value])
  selectedGameIds.value = []
  showBulkAddDialog.value = false
}

const filteredGames = computed(() => {
  if (!searchFilter.value) return props.availableGames
  return props.availableGames.filter(game => 
    game.game_name.toLowerCase().includes(searchFilter.value.toLowerCase())
  )
})

const toggleSelectAll = () => {
  if (selectedGameIds.value.length === filteredGames.value.length) {
    selectedGameIds.value = []
  } else {
    selectedGameIds.value = filteredGames.value.map(game => game.id)
  }
}

const handleOpenReorder = () => {
  reorderGames.value = [...props.selectedGames]
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

const handleSaveReorder = () => {
  emit('reorderGames', [...reorderGames.value])
  showReorderDialog.value = false
}

const handleCancelReorder = () => {
  showReorderDialog.value = false
  reorderGames.value = []
}
</script>