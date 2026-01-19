<template>
  <div class="gem-card p-2 bg-gray-900/40 rounded border border-gray-800 hover:border-gray-700 transition">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <div :class="['text-sm font-medium', gemColor]">
            {{ displayName }}
          </div>
          <span v-if="gem.is_support"
            class="text-xs px-1.5 py-0.5 bg-green-900/50 text-green-300 rounded">
            輔助
          </span>
          <span v-if="gem.is_awakened"
            class="text-xs px-1.5 py-0.5 bg-purple-900/50 text-purple-300 rounded">
            Awakened
          </span>
        </div>
        <div class="flex gap-2 mt-1 text-xs text-gray-500">
          <span>Lv {{ gem.level }}</span>
          <span v-if="gem.quality > 0">Q {{ gem.quality }}%</span>
          <span v-if="gem.quality_type !== 'DEFAULT'" class="text-purple-400">
            {{ gem.quality_type }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gem: { type: Object, required: true }
})

// 顯示名稱：輔助寶石加上 Support 後綴（如果原本沒有）
const displayName = computed(() => {
  const name = props.gem.name || ''
  if (props.gem.is_support && !name.toLowerCase().includes('support')) {
    return `${name} Support`
  }
  return name
})

// 顏色：輔助寶石綠色，覺醒寶石紫色，一般技能藍色
const gemColor = computed(() => {
  if (props.gem.is_awakened) return 'text-purple-400'
  if (props.gem.is_support) return 'text-green-400'
  return 'text-blue-400'
})
</script>
