<template>
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
        @click="handleAddGame"
        :disabled="!selectedGameId"
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
import { ref } from 'vue'
import type { Game } from '../types'
import type { GameAnalysis } from '../composables/useGameAnalysis'

interface Props {
  availableGames: Game[]
  selectedGames: GameAnalysis[]
}

interface Emits {
  (e: 'addGame', gameId: number): void
  (e: 'reorderGames', games: GameAnalysis[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const selectedGameId = ref('')
const showReorderDialog = ref(false)
const reorderGames = ref<GameAnalysis[]>([])

const handleAddGame = () => {
  if (selectedGameId.value) {
    emit('addGame', parseInt(selectedGameId.value))
    selectedGameId.value = ''
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