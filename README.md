# POE Build Simulator

Path of Exile 雙流派配置比對工具 - 比較兩個 Path of Building (PoB) 代碼，找出配置差異並產生改進建議。

> **核心原則**：此工具**僅專注於配置比較** - 不計算 DPS、生命值或其他數值。使用者需在 Path of Building 中自行驗證數值變化。

## 功能特色

- 解析 PoB 代碼（base64 + zlib 壓縮的 XML）
- 比較兩個 Build 的技能寶石、天賦樹、裝備配置
- 依優先級顯示差異（緊急 → 高 → 中 → 低）
- 提供具體的 PoB 操作步驟建議
- 整合 RePoE 資料驗證寶石分類

## 技術架構

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Tailwind CSS |
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

| 端點 | 說明 |
|------|------|
| `GET /api/health` | 健康檢查 |
| `POST /api/pob/parse-standardized` | 解析 PoB 代碼 |
| `POST /api/characters/compare` | 比較兩個 Build |
| `GET /api/passive-tree/init` | 初始化天賦樹資料 |

API 文件：http://localhost:8000/docs

## 開發進度

### 第一階段：寶石識別與顯示 ✅ 已完成
- 整合 RePoE 寶石資料 (`gem_service.py`)
- 修正輔助寶石識別（支援 457 個名稱變體）
- 前端顯示寶石名稱、等級、品質、輔助標籤

### 第二階段：按裝備部位展示寶石差異 🔄 進行中
- 擴展比對引擎，按裝備部位分組輸出
- 前端按部位顯示寶石差異 UI

### 第三階段：視覺化增強（規劃中）
- 整合 poe.ninja API 取得裝備圖示
- 優化比對結果呈現方式

## 專案結構

```
poe-build-simulator/
├── fastapi-service/          # FastAPI 後端
│   ├── app/
│   │   ├── main.py           # 應用程式入口
│   │   ├── pob_xml_mapper.py # PoB XML 解析
│   │   ├── gem_service.py    # RePoE 寶石資料服務
│   │   └── ...
│   └── data/repoe/           # RePoE JSON 資料（本地）
│
└── vue-frontend/             # Vue 3 前端
    └── src/
        ├── views/            # 頁面組件
        ├── components/       # UI 組件
        ├── stores/           # Pinia 狀態管理
        └── services/         # API 服務
```

## 版本歷史

- **v2.1.0** (2025-01): 整合 RePoE 寶石資料，修正輔助寶石識別
- **v2.0.0** (2025-12): 移除 Laravel，改用 Vue 直連 FastAPI 架構
- **v1.0.0** (2025-12): 初始版本

## 授權

MIT License
