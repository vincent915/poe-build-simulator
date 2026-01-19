<template>
  <div class="gem-card p-2 bg-gray-900/40 rounded border border-gray-800 hover:border-gray-700 transition">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <div :class="['text-sm font-medium', gemColor]">
            {{ gem.name }}
          </div>
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

const gemColor = computed(() => {
  return props.gem.is_awakened ? 'text-purple-400' : 'text-blue-400'
})
</script>
