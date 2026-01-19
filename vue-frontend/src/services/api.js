import axios from 'axios'

// 建立 axios 實例
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
})

// 請求攔截器
apiClient.interceptors.request.use(
    (config) => {
        console.log('🚀 API 請求:', config.method.toUpperCase(), config.url)
        return config
    },
    (requestError) => {
        console.error('❌ 請求錯誤:', requestError)
        return Promise.reject(requestError)
    }
)

// 回應攔截器
apiClient.interceptors.response.use(
    (response) => {
        console.log('✅ API 回應:', response.config.url, response.data)
        return response
    },
    (responseError) => {
        console.error('❌ 回應錯誤:', responseError.response?.data || responseError.message)
        return Promise.reject(responseError)
    }
)

// ===== API 方法 =====

export const poeApi = {
    // 測試連線
    testConnection() {
        return apiClient.get('/test')
    },

    // PoB 解析 API (呼叫 FastAPI)
    async parsePobCode(pobCode) {
        try {
            console.log('📋 解析 PoB 代碼:', pobCode.substring(0, 50) + '...')

            // 先嘗試呼叫 Laravel 的 PoB 解析端點
            const response = await apiClient.post('/build/parse-pob', {
                pob_code: pobCode
            })

            return response.data
        } catch (laravelError) {
            // 如果 Laravel 端點不存在，直接呼叫 FastAPI
            console.log('⚠️ Laravel PoB 解析失敗，嘗試直接呼叫 FastAPI')
            console.error('Laravel 錯誤詳情:', laravelError.message)

            try {
                const fastApiResponse = await axios.post('http://127.0.0.1:8001/api/pob/parse', {
                    pob_code: pobCode
                }, {
                    timeout: 30000,
                    headers: { 'Content-Type': 'application/json' }
                })

                return fastApiResponse.data
            } catch (fastApiError) {
                throw new Error(`PoB 解析失敗: ${fastApiError.response?.data?.message || fastApiError.message}`)
            }
        }
    },

    // 流派比對 API
    async compareBuild(data) {
        try {
            console.log('⚖️ 開始流派比對分析')

            const response = await apiClient.post('/build/compare-builds', data)
            return response.data
        } catch (compareError) {
            console.error('比對分析錯誤:', compareError.message)
            throw new Error(`比對分析失敗: ${compareError.response?.data?.message || compareError.message}`)
        }
    },

    // 備用：直接呼叫 FastAPI 進行比對
    async compareBuildDirect(data) {
        try {
            const fastApiResponse = await axios.post('http://127.0.0.1:8001/api/simulate', data, {
                timeout: 30000,
                headers: { 'Content-Type': 'application/json' }
            })

            return fastApiResponse.data
        } catch (directError) {
            console.error('FastAPI 直接呼叫錯誤:', directError.message)
            throw new Error(`FastAPI 比對失敗: ${directError.response?.data?.message || directError.message}`)
        }
    },

    // 天賦樹相關 API（保持原有功能）
    async getPassiveNodeInfo(nodeId) {
        const response = await apiClient.get(`/passive-tree/node/${nodeId}`)
        return response.data
    },

    async getPassiveNodesInfo(nodeIds) {
        const response = await apiClient.post('/passive-tree/nodes', {
            node_ids: nodeIds
        })
        return response.data
    },

    async calculatePassivePath(startNodes, targetNode) {
        const response = await apiClient.post('/passive-tree/path', {
            start_nodes: startNodes,
            target_node: targetNode
        })
        return response.data
    },

    async suggestPassivePaths(allocatedNodes, missingNodes, maxSuggestions = 5) {
        const response = await apiClient.post('/passive-tree/suggest-paths', {
            allocated_nodes: allocatedNodes,
            missing_nodes: missingNodes,
            max_suggestions: maxSuggestions
        })
        return response.data
    }
}

export default poeApi