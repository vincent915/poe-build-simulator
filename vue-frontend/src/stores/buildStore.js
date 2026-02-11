import { defineStore } from 'pinia'
import pobApi from '../services/pobApi'
import BuildDataTransformer from '../services/buildDataTransformer'

export const useBuildStore = defineStore('build', {
  state: () => ({
    playerBuild: null,
    targetBuild: null,
    playerPobCode: null,     // 保存原始 PoB 代碼
    targetPobCode: null,     // 保存原始 PoB 代碼
    comparisonResult: null,
    loading: false,
    error: null,
    currentStep: ''
  }),

  getters: {
    hasPlayerBuild: (state) => !!state.playerBuild,
    hasTargetBuild: (state) => !!state.targetBuild,
    canCompare: (state) => state.playerBuild && state.targetBuild,

    playerLevel: (state) => state.playerBuild?.stats?.level || 0,
    targetLevel: (state) => state.targetBuild?.stats?.level || 0,

    playerEquipmentGemMap: (state) => state.playerBuild?.equipmentGemMap || {},
    targetEquipmentGemMap: (state) => state.targetBuild?.equipmentGemMap || {},

    overallSimilarity: (state) => {
      return state.comparisonResult?.data?.overall_similarity?.overall || 0
    }
  },

  actions: {
    async loadPlayerBuild(pobCode) {
      this.loading = true
      this.currentStep = 'player'
      this.error = null

      try {
        console.log('開始解析玩家 PoB...')

        const result = await pobApi.parsePobCode(pobCode)

        if (result.status === 'success') {
          this.playerBuild = BuildDataTransformer.transformPobDataToBuild(result.data)
          this.playerPobCode = pobCode  // 保存原始 PoB 代碼
          console.log('玩家角色載入成功:', this.playerBuild)

          // 生成資料完整性報告（偵錯用）
          if (process.env.NODE_ENV === 'development') {
            console.log('--- 玩家角色資料報告 ---')
            BuildDataTransformer.generateDataReport(this.playerBuild)
          }

          return true
        } else {
          throw new Error(result.message || 'PoB 解析失敗')
        }
      } catch (error) {
        this.error = error.message
        console.error('載入玩家 PoB 失敗:', error)
        throw error
      } finally {
        this.loading = false
        this.currentStep = ''
      }
    },

    async loadTargetBuild(pobCode) {
      this.loading = true
      this.currentStep = 'target'
      this.error = null

      try {
        console.log('開始解析目標流派 PoB...')

        const result = await pobApi.parsePobCode(pobCode)

        if (result.status === 'success') {
          this.targetBuild = BuildDataTransformer.transformPobDataToBuild(result.data)
          this.targetPobCode = pobCode  // 保存原始 PoB 代碼
          console.log('目標流派載入成功:', this.targetBuild)

          // 生成資料完整性報告（偵錯用）
          if (process.env.NODE_ENV === 'development') {
            console.log('--- 目標流派資料報告 ---')
            BuildDataTransformer.generateDataReport(this.targetBuild)
          }

          return true
        } else {
          throw new Error(result.message || 'PoB 解析失敗')
        }
      } catch (error) {
        this.error = error.message
        console.error('載入目標 PoB 失敗:', error)
        throw error
      } finally {
        this.loading = false
        this.currentStep = ''
      }
    },

    async compareBuild() {
      if (!this.canCompare) {
        throw new Error('請先載入兩個流派')
      }

      if (!this.playerPobCode || !this.targetPobCode) {
        throw new Error('缺少 PoB 代碼')
      }

      this.loading = true
      this.currentStep = 'compare'
      this.error = null

      try {
        console.log('開始流派比對分析...')

        const result = await pobApi.compareBuild(
          this.playerPobCode,
          this.targetPobCode
        )

        if (result.status === 'success') {
          this.comparisonResult = result
          console.log('比對分析完成:', result)
          return true
        } else {
          throw new Error(result.message || '比對分析失敗')
        }
      } catch (error) {
        this.error = error.message
        console.error('流派比對失敗:', error)
        throw error
      } finally {
        this.loading = false
        this.currentStep = ''
      }
    },

    resetState() {
      this.playerBuild = null
      this.targetBuild = null
      this.playerPobCode = null
      this.targetPobCode = null
      this.comparisonResult = null
      this.error = null
      this.currentStep = ''
    }
  }
})