<template>
  <div v-if="hasCalculatedGames" class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface TotalStats {
  games: number
  results: number
  wins: number
  losses: number
  netAmount: number
}

interface MonthlyStats {
  month: string
  wins: number
  losses: number
  netAmount: number
}

interface Props {
  totalStats: TotalStats
  monthlyStats: MonthlyStats[]
  formatCurrency: (amount: number) => string
  getNetClass: (amount: number) => string
}

const props = defineProps<Props>()

const hasCalculatedGames = computed(() => props.totalStats.games > 0)
</script>