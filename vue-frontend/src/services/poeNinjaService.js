// poe.ninja API 服務 - 取得裝備圖示
// 使用 Vue reactive 讓組件能響應式更新圖示資料
import { reactive } from 'vue'

const CACHE_KEY = 'poe_ninja_icon_cache_v1'
const CACHE_TTL_MS = 24 * 60 * 60 * 1000  // 24 小時

// 聯盟名稱可透過 .env.local 的 VITE_POE_LEAGUE 覆蓋
const DEFAULT_LEAGUE = import.meta.env.VITE_POE_LEAGUE || 'Standard'

// poe.ninja 各物品類型（涵蓋所有 unique 裝備類別）
const ITEM_TYPES = [
  'UniqueWeapon',
  'UniqueArmour',
  'UniqueAccessory',
  'UniqueFlask',
  'UniqueJewel',
]

class PoeNinjaService {
  constructor() {
    // 使用 Vue reactive 讓 iconMap 具有響應式，組件能自動更新
    this.state = reactive({
      iconMap: null,   // { itemName: iconUrl }
      loading: false,
      loaded: false,
      error: null,
    })
    this._loadPromise = null
  }

  /**
   * 取得圖示 URL（同步，需先呼叫 ensureLoaded）
   */
  getIconUrl(itemName) {
    if (!this.state.iconMap || !itemName) return null
    return this.state.iconMap[itemName] || null
  }

  /**
   * 確保圖示資料已載入（可重複呼叫，只會執行一次）
   */
  async ensureLoaded() {
    if (this.state.loaded) return
    if (this._loadPromise) return this._loadPromise
    this._loadPromise = this._load()
    return this._loadPromise
  }

  /**
   * 載入圖示資料（優先使用快取）
   */
  async _load() {
    this.state.loading = true
    this.state.error = null

    try {
      // 嘗試讀取 localStorage 快取
      const cached = this._readCache()
      if (cached) {
        this.state.iconMap = cached
        this.state.loaded = true
        console.log(`[PoeNinja] 從快取載入 ${Object.keys(cached).length} 個圖示`)
        return
      }

      // 從 poe.ninja API 抓取
      const iconMap = {}
      console.log(`[PoeNinja] 開始抓取 ${DEFAULT_LEAGUE} 聯盟圖示資料...`)

      for (const type of ITEM_TYPES) {
        try {
          const url = `https://poe.ninja/api/data/itemoverview?league=${DEFAULT_LEAGUE}&type=${type}`
          const resp = await fetch(url, { signal: AbortSignal.timeout(10000) })
          if (!resp.ok) {
            console.warn(`[PoeNinja] ${type} 請求失敗: HTTP ${resp.status}`)
            continue
          }
          const data = await resp.json()
          let count = 0
          for (const item of (data.lines || [])) {
            if (item.name && item.icon) {
              iconMap[item.name] = item.icon
              count++
            }
          }
          console.log(`[PoeNinja] ${type}: 載入 ${count} 個圖示`)
        } catch (err) {
          console.warn(`[PoeNinja] 抓取 ${type} 失敗:`, err.message)
        }
      }

      // 儲存快取
      this._writeCache(iconMap)

      this.state.iconMap = iconMap
      this.state.loaded = true
      console.log(`[PoeNinja] 完成，共載入 ${Object.keys(iconMap).length} 個圖示`)
    } catch (err) {
      this.state.error = err.message
      console.error('[PoeNinja] 載入失敗:', err)
      // 即使失敗也標記為 loaded，避免無限重試
      this.state.iconMap = {}
      this.state.loaded = true
    } finally {
      this.state.loading = false
    }
  }

  _readCache() {
    try {
      const raw = localStorage.getItem(CACHE_KEY)
      if (!raw) return null
      const { data, timestamp, league } = JSON.parse(raw)
      // 快取過期或聯盟不符則視為無效
      if (Date.now() - timestamp > CACHE_TTL_MS) return null
      if (league !== DEFAULT_LEAGUE) return null
      return data
    } catch {
      return null
    }
  }

  _writeCache(iconMap) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        data: iconMap,
        timestamp: Date.now(),
        league: DEFAULT_LEAGUE,
      }))
    } catch (err) {
      console.warn('[PoeNinja] 快取寫入失敗:', err.message)
    }
  }

  clearCache() {
    localStorage.removeItem(CACHE_KEY)
    this.state.iconMap = null
    this.state.loaded = false
    this._loadPromise = null
  }

  get isLoading() {
    return this.state.loading
  }

  get isLoaded() {
    return this.state.loaded
  }
}

// 單例 export
export default new PoeNinjaService()
