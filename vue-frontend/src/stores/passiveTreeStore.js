import { defineStore } from 'pinia'
import apiClient from '../services/apiClient'

export const usePassiveTreeStore = defineStore('passiveTree', {
  state: () => ({
    allNodes: {},
    loaded: false,
    loading: false,
    error: null,
    selectedNode: null
  }),

  getters: {
    nodeCount: (state) => Object.keys(state.allNodes).length,
    isLoaded: (state) => state.loaded && state.nodeCount > 0
  },

  actions: {
    /**
     * 載入完整天賦樹資料
     */
    async loadTreeData() {
      if (this.loaded) {
        console.log('天賦樹資料已載入，使用快取')
        return
      }

      this.loading = true
      this.error = null

      try {
        console.log('載入天賦樹資料...')

        const response = await apiClient.get('/api/passive-tree/init')

        if (response.success) {
          this.loaded = true
          console.log('天賦樹資料載入成功:', response.node_count, '個節點')
        } else {
          throw new Error('天賦樹資料載入失敗')
        }
      } catch (error) {
        this.error = error.message
        console.error('載入天賦樹失敗:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * 取得節點資訊
     */
    async getNodeInfo(nodeId) {
      try {
        const response = await apiClient.get('/api/passive-tree/node/' + nodeId)

        if (response.success) {
          this.allNodes[nodeId] = response.node
          return response.node
        }
      } catch (error) {
        console.error('取得節點失敗 ID:', nodeId, error)
        return null
      }
    },

    /**
     * 批次取得多個節點資訊
     */
    async getNodesInfo(nodeIds) {
      try {
        const response = await apiClient.post('/api/passive-tree/nodes', {
          node_ids: nodeIds
        })

        if (response.success) {
          Object.assign(this.allNodes, response.nodes)
          return response.nodes
        }
      } catch (error) {
        console.error('批次取得節點失敗:', error)
        return {}
      }
    },

    /**
     * 計算路徑
     */
    async calculatePath(startNodes, targetNode) {
      try {
        const response = await apiClient.post('/api/passive-tree/path', {
          start_nodes: startNodes,
          target_node: targetNode
        })

        return response
      } catch (error) {
        console.error('計算路徑失敗:', error)
        return { success: false, message: error.message }
      }
    },

    /**
     * 路徑建議
     */
    async suggestPaths(allocatedNodes, missingNodes, maxSuggestions = 5) {
      try {
        const response = await apiClient.post('/api/passive-tree/suggest-paths', {
          allocated_nodes: allocatedNodes,
          missing_nodes: missingNodes,
          max_suggestions: maxSuggestions
        })

        return response
      } catch (error) {
        console.error('建議路徑失敗:', error)
        return { success: false, suggestions: [] }
      }
    }
  }
})