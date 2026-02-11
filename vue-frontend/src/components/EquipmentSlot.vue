<template>
  <div class="equipment-slot-wrapper">
    <div :class="[
      'equipment-slot rounded-lg border-2 transition-all',
      'bg-gray-900/50 hover:bg-gray-900/70',
      hasEquipment ? rarityBorder : 'border-gray-700',
      large ? 'p-4' : compact ? 'p-2' : 'p-3',
      'min-h-[80px]'
    ]">
      <!-- Empty -->
      <div v-if="!hasEquipment" class="text-center py-2">
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

      <!-- Gem toggle button (independent of equipment state) -->
      <button
        v-if="hasGems"
        @click.stop="expanded = !expanded"
        class="w-full mt-2 px-2 py-1 text-xs rounded bg-gray-800 hover:bg-gray-700 text-gray-300 transition flex items-center justify-center gap-1"
      >
        <span>{{ expanded ? '▲' : '▼' }}</span>
        <span>{{ totalGemCount }} 顆寶石</span>
      </button>
    </div>

    <!-- Gem groups (expandable) -->
    <div v-if="expanded && hasGems" class="mt-1 space-y-2">
      <div
        v-for="(group, gIdx) in gemGroups"
        :key="gIdx"
        class="bg-gray-800/60 rounded-lg p-2 border border-gray-700/50"
      >
        <div class="text-xs text-gray-400 mb-1 font-medium">
          {{ group.main_skill_name || group.label }}
          <span v-if="group.link_count" class="text-gray-500 ml-1">({{ group.link_count }}L)</span>
        </div>
        <div class="space-y-1">
          <GemCard
            v-for="(gem, gemIdx) in group.all_gems"
            :key="gemIdx"
            :gem="gem"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import SocketDisplay from './SocketDisplay.vue'
import GemCard from './GemCard.vue'

const props = defineProps({
  item: { type: Object, default: null },
  slotName: { type: String, required: true },
  emptyIcon: { type: String, default: '📦' },
  large: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
  gemGroups: { type: Array, default: () => [] }
})

const expanded = ref(false)

const hasEquipment = computed(() => {
  return props.item?.has_data === true
})

const hasGems = computed(() => {
  return props.gemGroups.length > 0
})

const totalGemCount = computed(() => {
  return props.gemGroups.reduce((sum, g) => sum + (g.all_gems?.length || 0), 0)
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
