# POE Build Simulator

Path of Exile 雙流派配置比對工具 - 比較兩個 Path of Building (PoB) 代碼，找出配置差異並產生改進建議。

> **核心原則**：此工具**僅專注於配置比較** - 不計算 DPS、生命值或其他數值。使用者需在 Path of Building 中自行驗證數值變化。

## 功能特色

- 解析 PoB 代碼（base64 + zlib 壓縮的 XML）
- 比較兩個 Build 的技能寶石、天賦樹、裝備配置
- 依優先級顯示差異（緊急 → 高 → 中 → 低）
- **按裝備部位分組展示寶石差異**（連結數、主技能、等級/品質）
- **裝備卡片顯示鑲嵌寶石**，支援展開/收合檢視
- 提供具體的 PoB 操作步驟建議
- 整合 RePoE 資料驗證寶石分類（支援 457 個輔助寶石名稱變體）

## 技術架構

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Tailwind CSS + Axios |
| 後端 | FastAPI (Python) |
| 資料來源 | RePoE (遊戲資料 JSON) |

## 快速開始

### 1. 啟動 FastAPI 後端
```bash
cd fastapi-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. 啟動 Vue 前端
```bash
cd vue-frontend
npm install
npm run dev
```

### 3. 開啟瀏覽器
訪問 http://localhost:5173

## 環境變數設定

在 `vue-frontend/.env.local` 設定：
```
VITE_FASTAPI_URL=http://127.0.0.1:8000
VITE_POE_SESSION_ID=your_session_id_here  # 選填
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查 |
| `/api/pob/parse-standardized` | POST | 解析 PoB 代碼，擷取配置 |
| `/api/characters/compare` | POST | 比較兩個 Build（參數：`player_pob_code`、`target_pob_code`） |
| `/api/passive-tree/init` | GET | 初始化天賦樹資料 |
| `/api/passive-tree/nodes` | POST | 批次取得節點資訊 |
| `/api/passive-tree/node/{node_id}` | GET | 單一節點資訊 |

API 文件：http://localhost:8000/docs

## 開發進度

### 第一階段：寶石識別與顯示 ✅ 已完成
- 整合 RePoE 寶石資料 (`gem_service.py`)
- 修正輔助寶石識別（支援 457 個名稱變體）
- 前端顯示寶石名稱、等級、品質、輔助標籤

### 第二階段：按裝備部位展示寶石差異 ✅ 已完成
- 實作 `/api/characters/compare` 端點
- 擴展比對引擎，按裝備部位分組輸出寶石差異
- 前端按部位顯示寶石差異 UI (`SlotGemComparison.vue`)
- 顯示連結數、主技能、寶石等級/品質差異

### 第三階段：視覺化增強 ⏳ 進行中
- ✅ 裝備卡片顯示鑲嵌寶石，支援展開/收合檢視
- 整合 poe.ninja API 取得裝備圖示
- 優化比對結果呈現方式
- 新增載入狀態與錯誤提示

### 第四階段：功能擴充（規劃中）
- 天賦樹路徑最佳化建議
- 裝備詞綴優先順序排序
- 使用者帳號與流派儲存

## 專案結構

```
poe-build-simulator/
├── fastapi-service/              # FastAPI 後端
│   ├── app/
│   │   ├── main.py               # 應用程式入口、路由
│   │   ├── pob_xml_mapper.py     # PoB XML 解析與資料標準化
│   │   ├── gem_service.py        # RePoE 寶石資料服務
│   │   ├── comparison_api_endpoints.py  # 比對 API 端點
│   │   ├── priority_comparison_engine.py # 優先級比對邏輯
│   │   ├── passive_tree_service.py      # 天賦樹服務
│   │   └── character_models.py   # 角色資料模型
│   ├── data/repoe/               # RePoE JSON 資料（本地）
│   └── requirements.txt
│
└── vue-frontend/                 # Vue 3 前端（單頁應用）
    └── src/
        ├── views/
        │   └── HomePage.vue      # 主頁面（PoB 輸入與比較顯示）
        ├── components/
        │   ├── SlotGemComparison.vue  # 按部位展示寶石差異
        │   ├── GemCard.vue       # 單一寶石卡片
        │   ├── CharacterStatsCard.vue # 角色資訊卡片
        │   ├── EquipmentGrid.vue # 裝備網格
        │   ├── EquipmentSlot.vue # 裝備卡片（含鑲嵌寶石展開/收合）
        │   └── SkillSetup.vue    # 技能設置顯示
        ├── stores/
        │   └── buildStore.js     # Build 比較狀態管理
        └── services/
            ├── api.js            # API 呼叫函數
            ├── pobApi.js         # PoB 解析 API
            └── buildDataTransformer.js # 資料轉換
```

## 版本歷史

- **v2.3.0** (2026-02): 裝備卡片顯示鑲嵌寶石，支援展開/收合檢視
- **v2.2.0** (2026-02): 完成第二階段 - 按裝備部位展示寶石差異；清理備份檔案與未使用的範本
- **v2.1.0** (2025-01): 整合 RePoE 寶石資料，修正輔助寶石識別
- **v2.0.0** (2025-12): 移除 Laravel，改用 Vue 直連 FastAPI 架構
- **v1.0.0** (2025-12): 初始版本

## 授權

MIT License
