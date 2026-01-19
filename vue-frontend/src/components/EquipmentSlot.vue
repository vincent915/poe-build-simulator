<template>
  <div :class="[
    'equipment-slot rounded-lg border-2 transition-all',
    'bg-gray-900/50 hover:bg-gray-900/70',
    hasEquipment ? rarityBorder : 'border-gray-700',
    large ? 'p-4' : compact ? 'p-2' : 'p-3',
    'min-h-[80px] flex items-center justify-center'
  ]">
    <!-- Empty -->
    <div v-if="!hasEquipment" class="text-center">
      <div class="text-2xl opacity-30 mb-1">{{ emptyIcon }}</div>
      <div class="text-xs text-gray-600">{{ slotName }}</div>
    </div>

    <!-- Equipped -->
    <div v-else class="w-full space-y-1">
      <div :class="['font-medium text-sm', rarityText]">
        {{ item.name || item.base_type }}
      </div>
      <div v-if="item.name && item.base_type" class="text-xs text-gray-400">
        {{ item.base_type }}
      </div>

      <!-- Sockets -->
      <SocketDisplay v-if="item.sockets?.max_links > 0" :sockets="item.sockets" />

      <!-- Influences -->
      <div v-if="hasInfluence" class="flex gap-1 text-xs">
        <span v-if="item.influences?.is_shaper" title="Shaper">🔵</span>
        <span v-if="item.influences?.is_elder" title="Elder">🟣</span>
        <span v-if="item.influences?.is_crusader" title="Crusader">⚪</span>
        <span v-if="item.influences?.is_hunter" title="Hunter">🟢</span>
      </div>

      <!-- Status -->
      <div v-if="item.is_corrupted" class="text-xs text-red-500">Corrupted</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SocketDisplay from './SocketDisplay.vue'

const props = defineProps({
  item: { type: Object, default: null },
  slotName: { type: String, required: true },
  emptyIcon: { type: String, default: '📦' },
  large: { type: Boolean, default: false },
  compact: { type: Boolean, default: false }
})

// 判斷是否有裝備（使用 has_data 字段）
const hasEquipment = computed(() => {
  return props.item?.has_data === true
})

const rarityText = computed(() => {
  const colors = {
    'NORMAL': 'text-gray-300',
    'MAGIC': 'text-blue-400',
    'RARE': 'text-yellow-400',
    'UNIQUE': 'text-orange-500'
  }
  return colors[props.item?.rarity] || 'text-gray-300'
})

const rarityBorder = computed(() => {
  const borders = {
    'NORMAL': 'border-gray-600',
    'MAGIC': 'border-blue-600',
    'RARE': 'border-yellow-600',
    'UNIQUE': 'border-orange-600'
  }
  return borders[props.item?.rarity] || 'border-gray-700'
})

const hasInfluence = computed(() => {
  if (!props.item?.influences) return false
  return Object.values(props.item.influences).some(v => v === true)
})
</script>
