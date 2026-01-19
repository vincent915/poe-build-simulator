<template>
    <div class="slot-gem-comparison">
        <h3 class="text-xl font-bold text-white mb-4">💎 按裝備部位的寶石差異</h3>

        <!-- 無資料提示 -->
        <div v-if="!slots || slots.length === 0" class="text-center py-8 text-gray-400">
            <p>沒有寶石配置資料</p>
        </div>

        <!-- 部位列表 -->
        <div v-else class="space-y-4">
            <div v-for="slot in slots" :key="slot.slot" :class="[
                'rounded-lg border p-4',
                slot.has_differences
                    ? 'bg-yellow-900/10 border-yellow-700/50'
                    : 'bg-gray-800/30 border-gray-700/50'
            ]">
                <!-- 部位標題 -->
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-3">
                        <span class="text-lg">{{ getSlotIcon(slot.slot) }}</span>
                        <div>
                            <h4 class="font-medium text-white">{{ slot.slot_label }}</h4>
                            <span class="text-xs text-gray-400">{{ slot.slot }}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-4">
                        <!-- 連結數比較 -->
                        <div class="text-sm">
                            <span class="text-blue-400">{{ slot.player_link_count }}L</span>
                            <span class="text-gray-500 mx-1">→</span>
                            <span class="text-purple-400">{{ slot.target_link_count }}L</span>
                        </div>
                        <!-- 差異數量標籤 -->
                        <span v-if="slot.has_differences" class="px-2 py-1 text-xs rounded bg-yellow-700/50 text-yellow-300">
                            {{ slot.gem_differences.length }} 項差異
                        </span>
                        <span v-else class="px-2 py-1 text-xs rounded bg-green-700/50 text-green-300">
                            一致
                        </span>
                    </div>
                </div>

                <!-- 展開/收合按鈕 -->
                <button @click="toggleSlot(slot.slot)"
                    class="w-full text-left text-sm text-gray-400 hover:text-white transition mb-3">
                    {{ expandedSlots[slot.slot] ? '▼ 收合詳情' : '▶ 展開詳情' }}
                </button>

                <!-- 詳細比較（展開時顯示） -->
                <div v-if="expandedSlots[slot.slot]" class="space-y-4">
                    <!-- 主技能比較 -->
                    <div v-if="slot.player_main_skill || slot.target_main_skill"
                        class="bg-gray-900/50 rounded p-3">
                        <div class="text-xs text-gray-500 mb-1">主技能</div>
                        <div class="flex items-center gap-2">
                            <span class="text-blue-400">{{ slot.player_main_skill || '無' }}</span>
                            <span class="text-gray-500">→</span>
                            <span class="text-purple-400">{{ slot.target_main_skill || '無' }}</span>
                        </div>
                    </div>

                    <!-- 寶石對比表格 -->
                    <div class="grid md:grid-cols-2 gap-4">
                        <!-- 玩家寶石 -->
                        <div class="bg-blue-900/10 border border-blue-700/30 rounded p-3">
                            <div class="text-xs text-blue-400 mb-2">你的寶石 ({{ slot.player_gems.length }})</div>
                            <div class="space-y-1">
                                <div v-for="gem in slot.player_gems" :key="gem.name"
                                    :class="['text-sm flex items-center justify-between', getGemClass(gem, slot.target_gems)]">
                                    <span :class="gem.is_support ? 'text-green-400' : 'text-blue-300'">
                                        {{ gem.name }}{{ gem.is_support ? ' Support' : '' }}
                                    </span>
                                    <span class="text-gray-400 text-xs">
                                        Lv{{ gem.level }} Q{{ gem.quality }}%
                                    </span>
                                </div>
                                <div v-if="slot.player_gems.length === 0" class="text-gray-500 text-sm">
                                    無寶石
                                </div>
                            </div>
                        </div>

                        <!-- 目標寶石 -->
                        <div class="bg-purple-900/10 border border-purple-700/30 rounded p-3">
                            <div class="text-xs text-purple-400 mb-2">目標寶石 ({{ slot.target_gems.length }})</div>
                            <div class="space-y-1">
                                <div v-for="gem in slot.target_gems" :key="gem.name"
                                    :class="['text-sm flex items-center justify-between', getGemClass(gem, slot.player_gems)]">
                                    <span :class="gem.is_support ? 'text-green-400' : 'text-purple-300'">
                                        {{ gem.name }}{{ gem.is_support ? ' Support' : '' }}
                                    </span>
                                    <span class="text-gray-400 text-xs">
                                        Lv{{ gem.level }} Q{{ gem.quality }}%
                                    </span>
                                </div>
                                <div v-if="slot.target_gems.length === 0" class="text-gray-500 text-sm">
                                    無寶石
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 差異列表 -->
                    <div v-if="slot.gem_differences.length > 0" class="space-y-2">
                        <div class="text-xs text-gray-500 mb-1">需要調整</div>
                        <div v-for="(diff, idx) in slot.gem_differences" :key="idx" :class="[
                            'p-2 rounded text-sm',
                            getPriorityClass(diff.priority)
                        ]">
                            <div class="flex items-start gap-2">
                                <span>{{ getPriorityIcon(diff.priority) }}</span>
                                <div class="flex-1">
                                    <p class="text-white">{{ diff.message }}</p>
                                    <p class="text-xs text-gray-400 mt-1">{{ diff.pob_instruction }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    slots: {
        type: Array,
        default: () => []
    }
})

// 展開狀態
const expandedSlots = ref({})

// 展開/收合
const toggleSlot = (slotName) => {
    expandedSlots.value[slotName] = !expandedSlots.value[slotName]
}

// 取得部位圖示
const getSlotIcon = (slot) => {
    const icons = {
        'Weapon 1': '⚔️',
        'Weapon 2': '🛡️',
        'Helmet': '🪖',
        'Body Armour': '🎽',
        'Gloves': '🧤',
        'Boots': '👢',
        'Amulet': '📿',
        'Ring 1': '💍',
        'Ring 2': '💍',
        'Belt': '🎗️'
    }
    return icons[slot] || '📦'
}

// 取得寶石樣式（標記缺少的寶石）
const getGemClass = (gem, otherGems) => {
    const exists = otherGems.some(g => g.name === gem.name)
    return exists ? '' : 'opacity-50 line-through'
}

// 取得優先級樣式
const getPriorityClass = (priority) => {
    const classes = {
        'critical': 'bg-red-900/30 border border-red-700/50',
        'high': 'bg-orange-900/30 border border-orange-700/50',
        'medium': 'bg-yellow-900/30 border border-yellow-700/50',
        'low': 'bg-blue-900/30 border border-blue-700/50'
    }
    return classes[priority] || 'bg-gray-800'
}

// 取得優先級圖示
const getPriorityIcon = (priority) => {
    const icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵'
    }
    return icons[priority] || '⚪'
}
</script>
