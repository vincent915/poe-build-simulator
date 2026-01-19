<template>
  <div :class="['rounded-lg p-4 border', borderColor, bgColor]">
    <h4 class="text-sm font-medium mb-3" :class="textColor">Basic Stats</h4>
    <div class="grid grid-cols-2 gap-2 text-sm">
      <div>
        <span class="text-gray-400">Level:</span>
        <span class="ml-2 text-white">{{ build.stats?.level }}</span>
      </div>
      <div>
        <span class="text-gray-400">Class:</span>
        <span class="ml-2 text-white">{{ build.stats?.character_class }}</span>
      </div>
      <div v-if="build.stats?.ascendancy" class="col-span-2">
        <span class="text-gray-400">Ascendancy:</span>
        <span class="ml-2 text-white">{{ build.stats?.ascendancy }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  build: { type: Object, required: true },
  color: { type: String, default: 'blue' }
})

const borderColor = computed(() =>
  props.color === 'blue' ? 'border-blue-700' : 'border-purple-700'
)
const bgColor = computed(() =>
  props.color === 'blue' ? 'bg-blue-900/20' : 'bg-purple-900/20'
)
const textColor = computed(() =>
  props.color === 'blue' ? 'text-blue-300' : 'text-purple-300'
)
</script>
