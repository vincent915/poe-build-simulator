"""
RePoE 寶石資料服務

載入 RePoE 的寶石資料，提供輔助寶石判斷與寶石資訊查詢功能。
"""

import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Set

logger = logging.getLogger(__name__)


class GemService:
    """寶石資料服務"""

    def __init__(self):
        self._gems_data: Dict = {}
        self._support_gem_names: Set[str] = set()
        self._display_name_to_key: Dict[str, str] = {}
        self._loaded = False

    def load_gem_data(self, data_dir: str = None) -> bool:
        """
        載入 RePoE 寶石資料

        Args:
            data_dir: 資料目錄路徑，預設為 data/repoe/

        Returns:
            是否載入成功
        """
        if self._loaded:
            return True

        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "repoe"
        else:
            data_dir = Path(data_dir)

        gems_file = data_dir / "gems_en.json"

        if not gems_file.exists():
            logger.warning(f"寶石資料檔案不存在: {gems_file}")
            return False

        try:
            with open(gems_file, "r", encoding="utf-8") as f:
                self._gems_data = json.load(f)

            # 建立輔助寶石名稱集合與顯示名稱映射
            for key, gem_info in self._gems_data.items():
                is_support = gem_info.get("is_support", False)
                display_name = gem_info.get("display_name", "")

                if not display_name:
                    continue

                display_name_lower = display_name.lower()

                # 建立顯示名稱到 key 的映射
                self._display_name_to_key[display_name_lower] = key

                # 收集輔助寶石的顯示名稱
                if is_support:
                    self._support_gem_names.add(display_name_lower)

                    # PoB 使用的名稱可能不含 "Support" 後綴
                    # 同時加入不含 "Support" 的版本
                    if display_name_lower.endswith(" support"):
                        name_without_support = display_name_lower[:-8]  # 移除 " support"
                        self._support_gem_names.add(name_without_support)
                        self._display_name_to_key[name_without_support] = key

            self._loaded = True
            logger.info(f"已載入 {len(self._gems_data)} 個寶石資料，"
                       f"其中 {len(self._support_gem_names)} 個輔助寶石名稱變體")
            return True

        except Exception as e:
            logger.error(f"載入寶石資料失敗: {e}")
            return False

    def is_support_gem(self, gem_name: str) -> bool:
        """
        判斷是否為輔助寶石

        Args:
            gem_name: 寶石名稱（顯示名稱）

        Returns:
            是否為輔助寶石
        """
        if not self._loaded:
            self.load_gem_data()

        # 直接用顯示名稱查詢
        return gem_name.lower() in self._support_gem_names

    def get_gem_info(self, gem_name: str) -> Optional[Dict]:
        """
        取得寶石完整資訊

        Args:
            gem_name: 寶石名稱（顯示名稱）

        Returns:
            寶石資訊字典，或 None
        """
        if not self._loaded:
            self.load_gem_data()

        key = self._display_name_to_key.get(gem_name.lower())
        if key:
            return self._gems_data.get(key)
        return None

    @property
    def support_gem_count(self) -> int:
        """輔助寶石數量"""
        return len(self._support_gem_names)

    @property
    def total_gem_count(self) -> int:
        """總寶石數量"""
        return len(self._gems_data)


@lru_cache(maxsize=1)
def get_gem_service() -> GemService:
    """取得單例 GemService"""
    service = GemService()
    service.load_gem_data()
    return service
