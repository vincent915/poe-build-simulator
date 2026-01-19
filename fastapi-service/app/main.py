"""
POE Build Simulator API - 重構版本
整合標準化角色比對架構
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# 設定日誌 - 修正為 __name__
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 引用新架構模組
from app.comparison_api_endpoints import register_comparison_routes
from app.passive_tree_service import passive_tree_service

# 建立 FastAPI 應用實例
app = FastAPI(
    title="POE Build Simulator API",
    version="3.0.0",
    description="角色裝備與天賦比對工具（標準化架構）"
)

# CORS 中間件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 建議開發時先用 ["*"]，上線再限縮
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 應用程式生命週期事件 =====
@app.on_event("startup")
async def startup_event():
    """應用啟動時預載入天賦樹資料"""
    logger.info("FastAPI 啟動中，預載入天賦樹資料...")
    passive_tree_service.load_tree_data()
    logger.info("天賦樹資料載入完成")

# ===== 基礎健康檢查端點 =====
@app.get("/")
def read_root():
    """根路徑健康檢查"""
    return {
        "message": "POE Build Simulator API",
        "status": "online",
        "version": "3.0.0 - Standardized Architecture"
    }

@app.get("/api/health")
def health_check():
    """詳細健康狀態檢查"""
    return {
        "status": "healthy",
        "service": "FastAPI POE Configuration Analyzer",
        "passive_tree_loaded": passive_tree_service.is_loaded(),
        "node_count": len(passive_tree_service.node_map)
    }

# ===== 天賦樹 API 端點 =====
@app.get("/api/passive-tree/init")
async def init_passive_tree():
    """手動初始化天賦樹資料"""
    success = passive_tree_service.load_tree_data()
    return {
        "success": success,
        "node_count": len(passive_tree_service.node_map),
        "loaded": passive_tree_service.is_loaded()
    }

@app.post("/api/passive-tree/nodes")
async def get_passive_nodes_info(request: dict):
    """批次取得天賦節點詳細資訊"""
    node_ids = request.get('node_ids', [])

    if not isinstance(node_ids, list):
        raise HTTPException(status_code=400, detail="node_ids must be an array")
    
    try:
        node_ids = [int(nid) for nid in node_ids]
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="All node_ids must be integers")
    
    nodes_info = passive_tree_service.get_nodes_info(node_ids)
    return {
        "success": True,
        "count": len(nodes_info),
        "nodes": nodes_info
    }

@app.get("/api/passive-tree/node/{node_id}")
async def get_passive_node_info(node_id: int):
    """取得單一節點詳細資訊"""
    node_info = passive_tree_service.get_node_info(node_id)
    return {
        "success": True, 
        "node": node_info
    }

@app.get("/api/passive-tree/status")
async def get_passive_tree_status():
    """檢查天賦樹資料載入狀態"""
    return {
        "loaded": passive_tree_service.is_loaded(),
        "node_count": len(passive_tree_service.node_map)
    }

@app.post("/api/passive-tree/path")
async def calculate_path(request: dict):
    """計算從已點節點到目標節點的最短路徑"""
    try:
        start_nodes = request.get('start_nodes', [])
        target_node = request.get('target_node')

        if not target_node:
            return {"success": False, "message": "Missing target_node"}
        
        result = passive_tree_service.calculate_path(start_nodes, target_node)
        return {
            "success": result.get('found', False),
            "path": result
        }
    except Exception as e:
        logger.error(f"計算路徑失敗: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/passive-tree/suggest-paths")
async def suggest_paths(request: dict):
    """建議最佳天賦路徑"""
    try:
        allocated_nodes = request.get('allocated_nodes', [])
        missing_nodes = request.get('missing_nodes', [])
        max_suggestions = request.get('max_suggestions', 5)

        suggestions = passive_tree_service.suggest_optimal_paths(
            allocated_nodes, 
            missing_nodes, 
            max_suggestions
        )
        return {
            "success": True,
            "count": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"建議路徑失敗: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

# ===== 註冊標準化角色比對路由 =====
register_comparison_routes(app)

# ===== 應用程式啟動配置 =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # 模組完整路徑
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
