import apiClient from './apiClient'

export default {
    async parsePobCode(pobCode) {
        try {
            const response = await apiClient.post('/api/pob/parse-standardized', {
                pob_code: pobCode
            })
            return response
        } catch (error) {
            // 提取 FastAPI 返回的詳細錯誤信息
            const errorMsg = error.response?.data?.detail?.user_message
                          || error.response?.data?.detail?.message
                          || error.response?.data?.message
                          || error.message
            throw new Error('PoB 解析失敗: ' + errorMsg)
        }
    },

    async compareBuild(playerPobCode, targetPobCode) {
        try {
            const response = await apiClient.post('/api/characters/compare', {
                player_pob_code: playerPobCode,
                target_pob_code: targetPobCode,
                lazy_load: true
            })
            return response
        } catch (error) {
            // 提取 FastAPI 返回的詳細錯誤信息
            const errorMsg = error.response?.data?.detail?.user_message
                          || error.response?.data?.detail?.message
                          || error.response?.data?.message
                          || error.message
            throw new Error('流派比對失敗: ' + errorMsg)
        }
    }
}