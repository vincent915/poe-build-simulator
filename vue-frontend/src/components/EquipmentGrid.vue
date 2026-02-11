<template>
  <div class="equipment-grid bg-gray-800/30 rounded-lg p-4 border border-gray-700">
    <h3 class="text-lg font-semibold text-gray-200 mb-3">{{ title }}</h3>

    <!-- Main Equipment -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <!-- Row 1 -->
      <EquipmentSlot :item="equipment.weapon_main_hand" slot-name="Main Hand" empty-icon="⚔️" :gem-groups="gemMap.weapon_main_hand || []" />
      <EquipmentSlot :item="equipment.helmet" slot-name="Helmet" empty-icon="🪖" :gem-groups="gemMap.helmet || []" />
      <EquipmentSlot :item="equipment.weapon_off_hand" slot-name="Off Hand" empty-icon="🛡️" :gem-groups="gemMap.weapon_off_hand || []" />

      <!-- Row 2: Body (spans 3) -->
      <div class="md:col-span-3">
        <EquipmentSlot :item="equipment.body_armour" slot-name="Body Armour" empty-icon="👕" large :gem-groups="gemMap.body_armour || []" />
      </div>

      <!-- Row 3 -->
      <EquipmentSlot :item="equipment.gloves" slot-name="Gloves" empty-icon="🧤" :gem-groups="gemMap.gloves || []" />
      <EquipmentSlot :item="equipment.belt" slot-name="Belt" empty-icon="🔗" :gem-groups="gemMap.belt || []" />
      <EquipmentSlot :item="equipment.boots" slot-name="Boots" empty-icon="👢" :gem-groups="gemMap.boots || []" />

      <!-- Row 4 -->
      <EquipmentSlot :item="equipment.ring_1" slot-name="Ring 1" empty-icon="💍" :gem-groups="gemMap.ring_1 || []" />
      <EquipmentSlot :item="equipment.amulet" slot-name="Amulet" empty-icon="📿" :gem-groups="gemMap.amulet || []" />
      <EquipmentSlot :item="equipment.ring_2" slot-name="Ring 2" empty-icon="💍" :gem-groups="gemMap.ring_2 || []" />
    </div>

    <!-- Flasks -->
    <div class="border-t border-gray-700 pt-4">
      <h4 class="text-sm font-medium text-gray-400 mb-2">Flasks</h4>
      <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <EquipmentSlot v-for="i in 5" :key="i"
          :item="equipment[`flask_${i}`]"
          :slot-name="`Flask ${i}`"
          empty-icon="🧪"
          compact
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import EquipmentSlot from './EquipmentSlot.vue'

defineProps({
  equipment: { type: Object, default: () => ({}) },
  gemMap: { type: Object, default: () => ({}) },
  title: { type: String, default: 'Equipment' }
})
</script>
