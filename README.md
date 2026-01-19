# POE Build Simulator v2.0

雙 PoB 流派比對分析工具

## 技術架構

- **前端**: Vue 3 + Pinia + Tailwind CSS
- **後端**: FastAPI (Python)
- **狀態管理**: Pinia
- **API 對接**: Axios

## 快速開始（Windows 10）

### 1. 啟動 FastAPI 後端
```powershell
cd fastapi-service
uvicorn app.main:app --reload --port 8001
```

### 2. 啟動 Vue 前端
```powershell
cd vue-frontend
npm install
npm run dev
```

### 3. 開啟瀏覽器

訪問 http://localhost:5173

## 環境變數設定

在 `vue-frontend\.env.local` 設定：
```
VITE_FASTAPI_URL=http://127.0.0.1:8001
VITE_POE_SESSION_ID=your_session_id_here
```

## 版本歷史

- **v2.0.0** (2025-12-21): 移除 Laravel，改用純前端架構
- **v1.0.0** (2025-12-15): 初始版本（Laravel + FastAPI + Vue）
