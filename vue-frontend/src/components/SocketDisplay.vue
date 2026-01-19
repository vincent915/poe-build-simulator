<template>
  <div class="flex items-center gap-1 flex-wrap">
    <div v-for="(group, idx) in sockets.groups" :key="idx" class="flex items-center gap-0.5">
      <div class="flex gap-0.5">
        <div v-for="(color, i) in group.colors" :key="i"
          :class="[
            'w-3 h-3 rounded-full border',
            getSocketColor(color),
            group.linked ? 'ring-1 ring-gray-400' : ''
          ]"
        />
      </div>
      <div v-if="idx < sockets.groups.length - 1" class="w-1 h-0.5 bg-gray-600 mx-1" />
    </div>
    <span v-if="sockets.max_links >= 4" class="text-xs text-gray-400 ml-1">
      {{ sockets.max_links }}L
    </span>
  </div>
</template>

<script setup>
defineProps({
  sockets: { type: Object, required: true }
})

function getSocketColor(color) {
  const colors = {
    'R': 'bg-red-600 border-red-700',
    'G': 'bg-green-600 border-green-700',
    'B': 'bg-blue-600 border-blue-700',
    'W': 'bg-gray-300 border-gray-400'
  }
  return colors[color] || 'bg-gray-700 border-gray-800'
}
</script>
