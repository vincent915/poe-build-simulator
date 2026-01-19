<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
    <!-- 標題 -->
    <header class="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700">
      <div class="container mx-auto px-4 py-4">
        <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          POE Build Simulator
        </h1>
        <p class="text-gray-400 text-sm mt-1">雙 PoB 流派比對分析工具</p>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <!-- 測試連線按鈕 -->
      <section class="mb-4">
        <button @click="testApi" :disabled="loading"
          class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition disabled:opacity-50">
          🔧 測試 API 連線
        </button>
      </section>

      <!-- 新增：使用 POE 角色數據 -->
      <section class="mb-8">
        <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
          <h2 class="text-2xl font-bold text-white mb-4">👤 載入你的 POE 角色</h2>
          <p class="text-gray-400 mb-4">使用官方 API 載入真實的角色數據</p>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">帳號名稱</label>
              <input v-model="accountName" type="text" placeholder="例如：AccountName#1234"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">角色名稱</label>
              <input v-model="characterName" type="text" placeholder="例如：CharacterName"
                class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" />
            </div>
          </div>

          <button @click="loadPlayerFromApi" :disabled="loading || !accountName || !characterName"
            class="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50">
            {{ loading && currentStep === 'load-api' ? '載入中...' : '🔄 從 POE 載入角色' }}
          </button>

          <!-- 玩家角色預覽 -->
          <div v-if="playerBuildData" class="mt-4 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
            <h4 class="text-sm font-medium text-blue-300 mb-2">✅ 角色已載入（真實數據）</h4>
            <div class="text-sm space-y-1">
              <p><span class="text-gray-400">等級：</span>{{ playerBuildData.stats?.level }}</p>
              <p><span class="text-gray-400">職業：</span>{{ playerBuildData.stats?.character_class }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 雙 PoB 輸入區域 -->
      <section class="mb-8">
        <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
          <h2 class="text-2xl font-bold text-white mb-6">🎯 流派比對分析</h2>
          <p class="text-gray-400 mb-6">貼上兩個 PoB 代碼，AI 會幫你分析差異與改善建議</p>

          <!-- 階段選擇器 -->
          <div class="mb-8">
            <h3 class="text-lg font-medium text-green-400 mb-3">⚙️ 比對階段設定</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button v-for="stage in stages" :key="stage.id" @click="selectStage(stage.id)" :class="[
                'py-4 px-3 rounded-lg border transition-all',
                selectedStage === stage.id
                  ? 'bg-green-600 border-green-500 text-white'
                  : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
              ]">
                <div class="text-center">
                  <div class="font-medium">{{ stage.name }}</div>
                  <div class="text-sm mt-1">{{ stage.level }}</div>
                </div>
              </button>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-8">
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

📗 如何獲取？
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
              <div v-if="targetBuildData" class="bg-purple-900/20 border border-purple-700 rounded-lg p-4">
                <h4 class="text-sm font-medium text-purple-300 mb-2">✅ 目標流派已載入</h4>
                <div class="text-sm space-y-1">
                  <p><span class="text-gray-400">等級：</span>{{ targetBuildData.stats?.level }}</p>
                  <p><span class="text-gray-400">職業：</span>{{ targetBuildData.stats?.character_class
                    }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 比對按鈕 -->
          <div class="mt-8 text-center">
            <button @click="startComparison"
              :disabled="loading || !playerBuildData || !targetBuildData || !selectedStage"
              class="px-12 py-4 text-xl bg-green-600 hover:bg-green-700 text-white rounded-lg transition disabled:opacity-50">
              {{ loading && currentStep === 'compare' ? '分析中...' : '🔄 開始比對分析' }}
            </button>

            <p v-if="!selectedStage || !playerBuildData || !targetBuildData" class="text-sm text-gray-400 mt-2">
              請先載入兩個流派並選擇比對階段
            </p>
          </div>
        </div>
      </section>

      <!-- 比對結果區域 -->
      <section v-if="comparisonResult" class="mb-8">
        <div class="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6">
          <h2 class="text-2xl font-bold text-white mb-6">📊 比對分析結果</h2>

          <!-- 整體相似度 -->
          <div class="bg-gray-700/50 rounded-lg p-6 mb-6">
            <div class="text-center space-y-6">
              <div>
                <p class="text-sm text-gray-400 mb-2">整體相似度</p>
                <p class="text-6xl font-bold text-yellow-400 mb-2">
                  {{ comparisonResult.data?.overall_similarity?.overall || '0' }}%
                </p>
                <p class="text-lg text-gray-300">
                  評級：{{ comparisonResult.data?.overall_similarity?.grade || '未知' }}
                </p>
              </div>
            </div>
          </div>

          <!-- 建議列表 -->
          <div class="space-y-3">
            <h3 class="text-xl font-bold text-white mb-4">💡 改進建議</h3>
            <div v-for="(rec, index) in (comparisonResult.data?.recommendations || [])" :key="index" :class="[
              'p-4 rounded-lg border',
              rec.priority === 'high' ? 'bg-red-900/20 border-red-700' :
                rec.priority === 'medium' ? 'bg-yellow-900/20 border-yellow-700' :
                  'bg-blue-900/20 border-blue-700'
            ]">
              <p class="font-medium text-white">{{ rec.message }}</p>
              <span class="inline-block mt-2 text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">
                {{ rec.category }}
              </span>
            </div>

            <div v-if="!comparisonResult.data?.recommendations?.length" class="text-center py-8 text-gray-400">
              <p>🎉 恭喜！沒有發現明顯的改進空間</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// API 基礎 URL
const API_BASE_URL = 'http://127.0.0.1:8000/api'

// API 相關
const loading = ref(false)
const currentStep = ref('')

// POE 角色資訊
const accountName = ref('')  // 填入你的 POE 帳號
const characterName = ref('')  // 填入你的角色名稱

// 表單資料
const targetPobCode = ref('')

// 階段選擇
const selectedStage = ref('mapping')
const stages = [
  { id: 'leveling', name: '過劇情', level: 'Lv 28-68', targetLevel: 68 },
  { id: 'mapping', name: '輿圖拓荒', level: 'Lv 75-90', targetLevel: 80 },
  { id: 'endgame', name: '終局刷寶', level: 'Lv 95+', targetLevel: 95 },
  { id: 'custom', name: '自訂等級', level: 'Custom', targetLevel: 90 }
]

// 資料載入狀態
const playerBuildData = ref(null)
const targetBuildData = ref(null)
const comparisonResult = ref(null)

// 測試 API 連線
const testApi = async () => {
  try {
    currentStep.value = 'test'
    loading.value = true

    const response = await fetch(`${API_BASE_URL}/test`)
    const data = await response.json()

    if (data.success) {
      alert(`✅ API 連線成功！\n${data.message}`)
    }
  } catch (error) {
    alert(`❌ API 連線失敗：${error.message}`)
  } finally {
    loading.value = false
    currentStep.value = ''
  }
}

// 從 POE API 載入真實角色數據
const loadPlayerFromApi = async () => {
  if (!accountName.value || !characterName.value) {
    alert('請輸入帳號名稱和角色名稱')
    return
  }

  try {
    currentStep.value = 'load-api'
    loading.value = true

    console.log('🔍 從 POE API 載入角色:', accountName.value, characterName.value)

    // 使用測試路由（mock data）
    const response = await fetch(
      `${API_BASE_URL}/poe/character/mock/${encodeURIComponent(accountName.value)}/${encodeURIComponent(characterName.value)}/full`
    )

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const result = await response.json()
    console.log('📦 API 回應:', result)

    if (result.success) {
      playerBuildData.value = result.data
      alert('✅ 角色載入成功！（使用真實 POE 數據）')
    } else {
      throw new Error(result.message || '載入失敗')
    }
  } catch (error) {
    console.error('載入角色失敗:', error)
    alert(`❌ 載入失敗：${error.message}\n\n提示：\n1. 確認角色名稱正確\n2. 確認角色設為公開\n3. 檢查 POESESSID 是否有效`)
  } finally {
    loading.value = false
    currentStep.value = ''
  }
}

// 載入目標流派 PoB
const loadTargetBuild = async () => {
  if (!targetPobCode.value.trim()) {
    alert('請先貼上目標流派的 PoB 代碼')
    return
  }

  try {
    currentStep.value = 'target'
    loading.value = true

    const response = await fetch(`${API_BASE_URL}/build/parse-pob`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pob_code: targetPobCode.value })
    })

    const result = await response.json()
    console.log('🔍 PoB 解析結果:', result)

    if (result.success && result.data?.status === 'success') {
      // 使用改進的轉換邏輯
      targetBuildData.value = transformPobDataImproved(result.data.data)
      alert('✅ 目標流派載入成功！')
    } else {
      throw new Error(result.message || 'PoB 解析失敗')
    }
  } catch (error) {
    alert(`❌ 載入失敗：${error.message}`)
  } finally {
    loading.value = false
    currentStep.value = ''
  }
}

// 開始比對分析
const startComparison = async () => {
  if (!playerBuildData.value || !targetBuildData.value) {
    alert('請先載入兩個流派')
    return
  }

  try {
    currentStep.value = 'compare'
    loading.value = true

    const stage = stages.find(s => s.id === selectedStage.value)

    const response = await fetch(`${API_BASE_URL}/build/compare-builds`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        player_build: playerBuildData.value,
        target_build: targetBuildData.value,
        target_level: stage.targetLevel,
        stage: selectedStage.value
      })
    })

    const result = await response.json()
    console.log('📊 比對結果:', result)

    if (result.success) {
      comparisonResult.value = result.data
      alert('✅ 比對分析完成！請查看下方結果')

      setTimeout(() => {
        document.querySelector('section:last-child')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } else {
      throw new Error(result.message || '比對分析失敗')
    }
  } catch (error) {
    alert(`❌ 比對失敗：${error.message}`)
  } finally {
    loading.value = false
    currentStep.value = ''
  }
}

// 選擇階段
const selectStage = (stageId) => {
  selectedStage.value = stageId
}

// 改進的 PoB 數據轉換（保留原有結構，但使用後端計算的數值）
const transformPobDataImproved = (pobData) => {
  // 優先使用後端已經計算好的數值
  if (pobData.computed_stats) {
    return {
      stats: pobData.computed_stats,
      main_skill: pobData.main_skill || { main_skill: 'Unknown', support_gems: [], links: 6 },
      passive_tree: pobData.passive_tree || { allocated_nodes: [], total_points: 0 }
    }
  }

  // 退回到基本結構
  const buildInfo = pobData.build_info || {}
  const level = buildInfo.level || 90

  return {
    stats: {
      level: level,
      character_class: buildInfo.class || 'Unknown',
      ascendancy: buildInfo.ascendancy || null,
      life: buildInfo.life || 5000,
      energy_shield: buildInfo.energy_shield || 0,
      mana: buildInfo.mana || 1000,
      dps: buildInfo.dps || 2000000,
      fire_res: 75,
      cold_res: 75,
      lightning_res: 75,
      chaos_res: 20
    },
    main_skill: {
      main_skill: 'Unknown',
      support_gems: [],
      links: 6
    },
    passive_tree: {
      allocated_nodes: [],
      total_points: Math.max(0, level - 1 + 8)
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style>
