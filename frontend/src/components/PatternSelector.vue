<template>
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
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Pattern {
  key: string
  label: string
  colorClass: string
  count: number
}

interface Props {
  selectedPatterns: string[]
  availablePatterns: Pattern[]
}

interface Emits {
  (e: 'update:selectedPatterns', value: string[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const selectedPatterns = computed({
  get: () => props.selectedPatterns,
  set: (value) => emit('update:selectedPatterns', value)
})
</script>