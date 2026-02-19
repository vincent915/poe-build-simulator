# POE Build Simulator - Vue 前端

此目錄為 POE Build Simulator 的 Vue 3 前端。

完整專案說明請參閱根目錄 [README.md](../README.md)。

## 快速開始

```bash
npm install
npm run dev      # 開發伺服器 localhost:5173
npm run build    # 正式環境建置
npm run lint     # ESLint 檢查
```

需同時啟動後端服務：

```bash
cd ../fastapi-service
uvicorn app.main:app --reload --port 8000
```

## 環境變數

建立 `.env.local`：

```
VITE_FASTAPI_URL=http://127.0.0.1:8000
```
