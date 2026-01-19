<template>
  <div class="skill-setup bg-gray-800/30 rounded-lg p-4 border border-gray-700">
    <h3 class="text-lg font-semibold text-gray-200 mb-3">{{ title }}</h3>

    <div v-if="mainSkillGroup" class="space-y-3">
      <!-- Header -->
      <div class="flex items-center justify-between text-sm text-gray-400">
        <span>{{ mainSkillGroup.label }}</span>
        <span>{{ mainSkillGroup.slot }} • {{ mainSkillGroup.link_count }}L</span>
      </div>

      <!-- Main Skill -->
      <div v-if="mainSkillGroup.main_skill"
        class="bg-gray-900/50 rounded-lg p-3 border border-green-700">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="font-medium text-green-400">
              {{ mainSkillGroup.main_skill.name }}
            </div>
            <div class="flex gap-2 mt-1 text-xs text-gray-400">
              <span>Level {{ mainSkillGroup.main_skill.level }}</span>
              <span v-if="mainSkillGroup.main_skill.quality > 0">
                Quality {{ mainSkillGroup.main_skill.quality }}%
              </span>
              <span v-if="mainSkillGroup.main_skill.quality_type !== 'DEFAULT'"
                class="text-purple-400">
                {{ mainSkillGroup.main_skill.quality_type }}
              </span>
            </div>
          </div>
          <div v-if="mainSkillGroup.main_skill.is_vaal"
            class="text-xs px-2 py-1 bg-red-900/30 text-red-400 rounded">
            Vaal
          </div>
        </div>
      </div>

      <!-- Support Gems -->
      <div v-if="mainSkillGroup.support_gems?.length > 0" class="space-y-2">
        <div class="text-xs text-gray-500 uppercase tracking-wider">
          Support Gems ({{ mainSkillGroup.support_gems.length }})
        </div>
        <div class="grid gap-2">
          <GemCard v-for="(gem, i) in mainSkillGroup.support_gems" :key="i" :gem="gem" />
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8 text-gray-500">
      <div class="text-3xl mb-2">💎</div>
      <div class="text-sm">No main skill configured</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import GemCard from './GemCard.vue'

const props = defineProps({
  skills: { type: Object, required: true },
  title: { type: String, default: 'Skills' }
})

const mainSkillGroup = computed(() => props.skills?.main_skill_group || null)
</script>
