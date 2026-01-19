<template>
    <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <!-- 標題 -->
        <header class="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700">
            <div class="container mx-auto px-4 py-4">
                <h1
                    class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    POE 流派配置分析工具
                </h1>
                <p class="text-gray-400 text-sm mt-1">找出配置差異 → 在 PoB 驗證 → 遊戲中實踐</p>
            </div>
        </header>

        <main class="container mx-auto px-4 py-8">
            <!-- 雙 PoB 輸入區域 -->
            <section class="mb-8">
                <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
                    <h2 class="text-2xl font-bold text-white mb-6">🎯 流派配置比對</h2>
                    <p class="text-gray-400 mb-6">貼上兩個 PoB 代碼，分析配置差異並生成改進清單</p>

                    <div class="grid md:grid-cols-2 gap-8">
                        <!-- 你的角色 PoB -->
                        <div class="space-y-4">
                            <div class="flex items-center gap-3 mb-4">
                                <span class="text-2xl">🧑‍💼</span>
                                <h3 class="text-xl font-medium text-blue-400">你的角色</h3>
                            </div>

                            <div class="space-y-3">
                                <label class="block text-sm font-medium text-gray-300">
                                    Path of Building 代碼
                                </label>
                                <textarea v-model="playerPobCode" placeholder="請貼上你的 PoB 代碼...

                                🔗 如何獲取？
                                1. 開啟 Path of Building
                                2. 匯入你的角色
                                3. 點擊「匯出至剪貼板」
                                4. 貼上到這裡" rows="8"
                                    class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono text-sm"></textarea>

                                <button @click="loadPlayerBuild" :disabled="loading || !playerPobCode"
                                    class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50">
                                    {{ loading && currentStep === 'player' ? '解析中...' : '🔄 載入我的角色' }}
                                </button>
                            </div>

                            <!-- 玩家角色預覽 -->
                            <div v-if="playerBuild" class="bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                                <h4 class="text-sm font-medium text-blue-300 mb-2">✅ 角色已載入</h4>
                                <div class="text-sm space-y-1">
                                    <p><span class="text-gray-400">等級：</span>{{ playerBuild.stats?.level }}</p>
                                    <p><span class="text-gray-400">職業：</span>{{ playerBuild.stats?.character_class }}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- 目標流派 PoB -->
                        <div class="space-y-4">
                            <div class="flex items-center gap-3 mb-4">
                                <span class="text-2xl">🎯</span>
                                <h3 class="text-xl font-medium text-purple-400">目標流派</h3>
                            </div>

                            <div class="space-y-3">
                                <label class="block text-sm font-medium text-gray-300">
                                    目標流派 PoB 代碼
                                </label>
                                <textarea v-model="targetPobCode" placeholder="請貼上目標流派的 PoB 代碼...

                                🔗 如何獲取？
                                1. 從 poe.ninja 找高手流派
                                2. 點擊「PoB」按鈕
                                3. 複製代碼貼上到這裡" rows="8"
                                    class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none font-mono text-sm"></textarea>

                                <button @click="loadTargetBuild" :disabled="loading || !targetPobCode"
                                    class="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition disabled:opacity-50">
                                    {{ loading && currentStep === 'target' ? '解析中...' : '🔄 載入目標流派' }}
                                </button>
                            </div>

                            <!-- 目標流派預覽 -->
                            <div v-if="targetBuild" class="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
                                <h4 class="text-sm font-medium text-purple-300 mb-2">✅ 目標流派已載入</h4>
                                <div class="text-sm space-y-1">
                                    <p><span class="text-gray-400">等級：</span>{{ targetBuild.stats?.level }}</p>
                                    <p><span class="text-gray-400">職業：</span>{{ targetBuild.stats?.character_class }}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 比對按鈕 -->
                    <div class="mt-8 text-center">
                        <button @click="startComparison" :disabled="loading || !playerBuild || !targetBuild"
                            class="px-12 py-4 text-xl bg-green-600 hover:bg-green-700 text-white rounded-lg transition disabled:opacity-50">
                            {{ loading && currentStep === 'compare' ? '分析中...' : '🔮 開始配置比對' }}
                        </button>

                        <p v-if="!playerBuild || !targetBuild" class="text-sm text-gray-400 mt-2">
                            請先載入兩個流派
                        </p>
                    </div>
                </div>
            </section>

            <!-- 角色預覽與比對區域 -->
            <section v-if="playerBuild || targetBuild" class="mb-8">
                <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
                    <h2 class="text-2xl font-bold text-white mb-6">⚖️ Character Comparison</h2>

                    <div class="grid md:grid-cols-2 gap-6">
                        <!-- 玩家角色欄 -->
                        <div v-if="playerBuild" class="space-y-4">
                            <div class="flex items-center gap-2 mb-4">
                                <span class="text-xl">🧑‍💼</span>
                                <h3 class="text-lg font-semibold text-blue-400">Your Character</h3>
                            </div>

                            <CharacterStatsCard :build="playerBuild" color="blue" />
                            <EquipmentGrid :equipment="playerBuild.equipment || {}" title="Equipment" />
                            <SkillSetup :skills="playerBuild.skills || {}" title="Skills" />
                        </div>

                        <!-- 目標流派欄 -->
                        <div v-if="targetBuild" class="space-y-4">
                            <div class="flex items-center gap-2 mb-4">
                                <span class="text-xl">🎯</span>
                                <h3 class="text-lg font-semibold text-purple-400">Target Build</h3>
                            </div>

                            <CharacterStatsCard :build="targetBuild" color="purple" />
                            <EquipmentGrid :equipment="targetBuild.equipment || {}" title="Equipment" />
                            <SkillSetup :skills="targetBuild.skills || {}" title="Skills" />
                        </div>
                    </div>
                </div>
            </section>

            <!-- 比對結果區域 -->
            <section v-if="comparisonResult" class="mb-8">
                <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
                    <h2 class="text-2xl font-bold text-white mb-6">📊 配置差異分析</h2>

                    <!-- 摘要統計 -->
                    <div v-if="comparisonResult.summary" class="mb-6 grid grid-cols-2 md:grid-cols-5 gap-3">
                        <div class="bg-red-900/20 border border-red-700 rounded-lg p-3 text-center">
                            <div class="text-2xl font-bold text-red-400">{{ comparisonResult.summary.critical_count || 0 }}</div>
                            <div class="text-xs text-gray-400">嚴重問題</div>
                        </div>
                        <div class="bg-orange-900/20 border border-orange-700 rounded-lg p-3 text-center">
                            <div class="text-2xl font-bold text-orange-400">{{ comparisonResult.summary.high_count || 0 }}</div>
                            <div class="text-xs text-gray-400">高優先級</div>
                        </div>
                        <div class="bg-yellow-900/20 border border-yellow-700 rounded-lg p-3 text-center">
                            <div class="text-2xl font-bold text-yellow-400">{{ comparisonResult.summary.medium_count || 0 }}</div>
                            <div class="text-xs text-gray-400">中優先級</div>
                        </div>
                        <div class="bg-blue-900/20 border border-blue-700 rounded-lg p-3 text-center">
                            <div class="text-2xl font-bold text-blue-400">{{ comparisonResult.summary.low_count || 0 }}</div>
                            <div class="text-xs text-gray-400">低優先級</div>
                        </div>
                        <div class="bg-gray-700/30 border border-gray-600 rounded-lg p-3 text-center">
                            <div class="text-2xl font-bold text-white">{{ comparisonResult.summary.total_issues || 0 }}</div>
                            <div class="text-xs text-gray-400">總差異數</div>
                        </div>
                    </div>

                    <!-- 改進建議 -->
                    <div class="space-y-3">
                        <h3 class="text-xl font-bold text-white mb-4">💡 改進清單</h3>

                        <div v-for="(rec, index) in (comparisonResult.differences || [])" :key="index" :class="[
                            'p-4 rounded-lg border',
                            rec.priority === 'critical' ? 'bg-red-900/20 border-red-700' :
                                rec.priority === 'high' ? 'bg-orange-900/20 border-orange-700' :
                                    rec.priority === 'medium' ? 'bg-yellow-900/20 border-yellow-700' :
                                        'bg-blue-900/20 border-blue-700'
                        ]">
                            <div class="flex items-start gap-3">
                                <span class="text-2xl">
                                    {{ rec.priority === 'critical' ? '🔴' :
                                        rec.priority === 'high' ? '🟠' :
                                            rec.priority === 'medium' ? '🟡' : '🔵' }}
                                </span>
                                <div class="flex-1">
                                    <p class="font-medium text-white mb-1">{{ rec.message }}</p>
                                    <p class="text-sm text-gray-300 mb-2">{{ rec.action }}</p>
                                    <div class="bg-gray-900/50 p-2 rounded text-xs text-gray-400">
                                        💡 PoB 操作：{{ rec.pob_instruction }}
                                    </div>
                                    <span class="inline-block mt-2 text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">
                                        {{ rec.category }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div v-if="!comparisonResult.differences?.length"
                            class="text-center py-8 text-gray-400">
                            <p>🎉 恭喜！沒有發現明顯的改進空間</p>
                        </div>
                    </div>

                    <!-- 重要提示 -->
                    <div class="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
                        <h4 class="text-lg font-bold text-blue-300 mb-2">📌 下一步行動</h4>
                        <ol class="text-sm text-gray-300 space-y-2 list-decimal list-inside">
                            <li>在 Path of Building 中按照上述建議逐項調整</li>
                            <li>在 PoB 中觀察調整後的數值變化</li>
                            <li>確認改進效果後再在遊戲中執行</li>
                        </ol>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useBuildStore } from '@/stores/buildStore'
import EquipmentGrid from '@/components/EquipmentGrid.vue'
import SkillSetup from '@/components/SkillSetup.vue'
import CharacterStatsCard from '@/components/CharacterStatsCard.vue'

// ===== Pinia Store =====
const buildStore = useBuildStore()
const {
    playerBuild,
    targetBuild,
    comparisonResult,
    loading,
    currentStep,
    canCompare
} = storeToRefs(buildStore)

// ===== 本地狀態（僅保留真正需要的） =====
const playerPobCode = ref('')
const targetPobCode = ref('')

// ===== 方法 =====
const loadPlayerBuild = async () => {
    if (!playerPobCode.value.trim()) {
        alert('請先貼上你的 PoB 代碼')
        return
    }

    try {
        await buildStore.loadPlayerBuild(playerPobCode.value)
        alert('✅ 你的角色載入成功！')
    } catch (error) {
        alert('❌ 載入失敗：' + error.message)
    }
}

const loadTargetBuild = async () => {
    if (!targetPobCode.value.trim()) {
        alert('請先貼上目標流派的 PoB 代碼')
        return
    }

    try {
        await buildStore.loadTargetBuild(targetPobCode.value)
        alert('✅ 目標流派載入成功！')
    } catch (error) {
        alert('❌ 載入失敗：' + error.message)
    }
}

const startComparison = async () => {
    if (!canCompare.value) {
        alert('請先載入兩個流派')
        return
    }

    try {
        await buildStore.compareBuild()
        alert('✅ 比對分析完成！請查看下方結果')

        // 滾動到結果區域
        setTimeout(() => {
            const resultSection = document.querySelector('section:last-child')
            if (resultSection) {
                resultSection.scrollIntoView({ behavior: 'smooth' })
            }
        }, 100)
    } catch (error) {
        alert('❌ 比對失敗：' + error.message)
    }
}
</script>

<style scoped>
/* 自定義樣式 */
.container {
    max-width: 1200px;
}
</style>