"""
FastAPI 端點整合
將標準化流程整合到 API 層
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import base64
import zlib
import xml.etree.ElementTree as ET
import logging

from app.character_models import StandardizedCharacter
from app.pob_xml_mapper import PobXmlMapper
from app.priority_comparison_engine import (
    PriorityComparisonEngine,
    ComparisonDifference,
    SlotGemDifference
)

logger = logging.getLogger(__name__)


# ===== 請求/回應模型 =====

class PobCodeRequest(BaseModel):
    """PoB 代碼請求"""
    pob_code: str


class CharacterComparisonRequest(BaseModel):
    """角色比對請求"""
    player_pob_code: str
    target_pob_code: str
    lazy_load: bool = True


class ComparisonResponse(BaseModel):
    """比對結果回應"""
    status: str
    message: str
    player_character: Dict[str, Any]
    target_character: Dict[str, Any]
    differences: List[Dict[str, Any]]
    gem_differences_by_slot: List[Dict[str, Any]]  # 按裝備部位分組的寶石差異
    summary: Dict[str, Any]


# ===== 核心服務函數 =====

def decode_and_parse_pob(pob_code: str) -> ET.Element:
    """
    解碼並解析 PoB 代碼
    
    Args:
        pob_code: Base64 編碼的 PoB 字串
        
    Returns:
        XML 根節點
        
    Raises:
        ValueError: 解碼或解析失敗
    """
    try:
        # 清理代碼
        pob_code_clean = pob_code.replace(' ', '').replace('\n', '').replace('\r', '')
        
        # 補齊 padding
        missing_padding = len(pob_code_clean) % 4
        if missing_padding:
            pob_code_clean += '=' * (4 - missing_padding)
        
        # Base64 解碼
        try:
            decoded = base64.urlsafe_b64decode(pob_code_clean)
        except Exception:
            decoded = base64.b64decode(pob_code_clean)
        
        # Zlib 解壓縮
        try:
            decompressed = zlib.decompress(decoded)
        except zlib.error:
            decompressed = zlib.decompress(decoded, -zlib.MAX_WBITS)
        
        # XML 解析
        xml_string = decompressed.decode('utf-8')
        root = ET.fromstring(xml_string)
        
        return root
        
    except Exception as e:
        logger.error(f"PoB 解析失敗: {str(e)}")
        raise ValueError(f"PoB 代碼解析失敗: {str(e)}")


def standardize_character_from_pob(
    pob_code: str,
    lazy_load: bool = True
) -> StandardizedCharacter:
    """
    從 PoB 代碼標準化角色資料
    
    Args:
        pob_code: PoB 代碼
        lazy_load: 是否惰性載入
        
    Returns:
        標準化角色物件
    """
    # 解析 XML
    root = decode_and_parse_pob(pob_code)
    
    # 轉換為標準化格式
    mapper = PobXmlMapper()
    character = mapper.extract_standardized_character(root, lazy_load)
    
    return character


def compare_characters_with_priority(
    player_character: StandardizedCharacter,
    target_character: StandardizedCharacter
) -> tuple[List[ComparisonDifference], List[SlotGemDifference]]:
    """
    執行優先級比對

    Args:
        player_character: 玩家角色
        target_character: 目標角色

    Returns:
        (差異列表, 按裝備部位分組的寶石差異)
    """
    engine = PriorityComparisonEngine()
    differences = engine.compare_characters(player_character, target_character)
    gem_differences_by_slot = engine.get_gem_differences_by_slot()

    return differences, gem_differences_by_slot


def generate_comparison_summary(
    differences: List[ComparisonDifference]
) -> Dict[str, Any]:
    """
    生成比對摘要
    
    Args:
        differences: 差異列表
        
    Returns:
        摘要資訊
    """
    summary = {
        "total_issues": len(differences),
        "critical_count": len([d for d in differences if d['priority'] == 'critical']),
        "high_count": len([d for d in differences if d['priority'] == 'high']),
        "medium_count": len([d for d in differences if d['priority'] == 'medium']),
        "low_count": len([d for d in differences if d['priority'] == 'low']),
        "categories": {}
    }
    
    # 統計各類別數量
    for diff in differences:
        category = diff['category']
        if category not in summary['categories']:
            summary['categories'][category] = 0
        summary['categories'][category] += 1
    
    return summary


# ===== API 端點函數 =====

async def parse_pob_endpoint(request: PobCodeRequest) -> Dict[str, Any]:
    """
    PoB 解析端點（整合標準化流程）
    
    Args:
        request: PoB 請求
        
    Returns:
        標準化角色資料
    """
    try:
        character = standardize_character_from_pob(request.pob_code)
        
        return {
            "status": "success",
            "message": "PoB 解析成功",
            "data": character.dict(),
            "note": "已轉換為標準化內部格式"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "parse_error",
                "message": str(e),
                "user_message": "PoB 代碼解析失敗，請確認代碼是否完整"
            }
        )
    except Exception as e:
        logger.error(f"未預期錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "internal_error",
                "message": str(e),
                "user_message": "系統處理錯誤"
            }
        )


async def compare_characters_endpoint(
    request: CharacterComparisonRequest
) -> ComparisonResponse:
    """
    角色比對端點（整合優先級引擎）

    Args:
        request: 比對請求

    Returns:
        比對結果
    """
    try:
        # 解析並標準化兩個角色
        logger.info("解析玩家角色")
        player_character = standardize_character_from_pob(
            request.player_pob_code,
            request.lazy_load
        )

        logger.info("解析目標角色")
        target_character = standardize_character_from_pob(
            request.target_pob_code,
            request.lazy_load
        )

        # 執行優先級比對
        logger.info("執行優先級比對分析")
        differences, gem_differences_by_slot = compare_characters_with_priority(
            player_character,
            target_character
        )

        # 生成摘要
        summary = generate_comparison_summary(differences)

        # 統計有差異的裝備部位數量
        slots_with_diff = len([s for s in gem_differences_by_slot if s.get('has_differences')])
        logger.info(f"按裝備部位比較完成，{len(gem_differences_by_slot)} 個部位，"
                   f"{slots_with_diff} 個部位有差異")

        return ComparisonResponse(
            status="success",
            message=f"比對完成，發現 {len(differences)} 項差異",
            player_character=player_character.dict(),
            target_character=target_character.dict(),
            differences=[dict(d) for d in differences],
            gem_differences_by_slot=[dict(s) for s in gem_differences_by_slot],
            summary=summary
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "parse_error",
                "message": str(e),
                "user_message": "PoB 代碼解析失敗"
            }
        )
    except Exception as e:
        logger.error(f"比對錯誤: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": "comparison_error",
                "message": str(e),
                "user_message": "角色比對失敗"
            }
        )


# ===== 註冊路由範例 =====

def register_comparison_routes(app: FastAPI):
    """
    註冊比對相關路由
    
    Args:
        app: FastAPI 應用實例
    """
    
    @app.post("/api/pob/parse-standardized")
    async def parse_pob_standardized(request: PobCodeRequest):
        """解析 PoB 並返回標準化格式"""
        return await parse_pob_endpoint(request)
    
    @app.post("/api/characters/compare")
    async def compare_characters(request: CharacterComparisonRequest):
        """比對兩個角色並返回優先級差異"""
        return await compare_characters_endpoint(request)