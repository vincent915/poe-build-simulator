"""
PoB XML 結構化提取器
將 PoB 的 XML 結構轉換為標準化內部格式
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

from app.character_models import (
    StandardizedCharacter,
    CharacterCore,
    PassiveAllocation,
    SkillSetup,
    EquipmentSnapshot,
    SkillGroup,
    GemInfo,
    EquipmentItem,
    ItemModifier,
    SocketGroup,
    JewelSocketInfo,
    AscendancyStatus,
    GemQualityType,
    ItemRarity,
    SocketColor
)
from app.gem_service import get_gem_service

logger = logging.getLogger(__name__)


class PobXmlMapper:
    """PoB XML 節點映射器"""
    
    # 支援的 PoB 版本
    SUPPORTED_VERSIONS = {
        "official": "1.4",  # 官方版本
        "community": "2.0"  # 社群 Fork 版本
    }
    
    def __init__(self):
        """初始化映射器"""
        self.version_detected = None
        self.compatibility_mode = "auto"
    
    def detect_pob_version(self, root: ET.Element) -> str:
        """
        檢測 PoB 版本
        
        Args:
            root: XML 根節點
            
        Returns:
            版本類型: 'official' 或 'community'
        """
        # 檢查是否存在社群版本特有的節點
        calcs = root.find(".//Calcs")
        if calcs is not None:
            logger.info("檢測到社群 Fork 版本（存在 Calcs 節點）")
            return "community"
        
        # 預設為官方版本
        logger.info("檢測為官方版本")
        return "official"
    
    def extract_standardized_character(
        self,
        root: ET.Element,
        lazy_load: bool = True
    ) -> StandardizedCharacter:
        """
        從 XML 提取標準化角色資料
        
        Args:
            root: XML 根節點
            lazy_load: 是否使用惰性載入（優先載入核心資料）
            
        Returns:
            標準化角色物件
        """
        # 檢測版本
        self.version_detected = self.detect_pob_version(root)
        
        # 提取核心資料（第一優先級）
        character_core = self._extract_character_core(root)
        
        if lazy_load:
            logger.info("使用惰性載入模式，優先載入核心資料")
        
        # 提取天賦樹（第一優先級）
        passive_allocation = self._extract_passive_allocation(root)
        
        # 提取技能配置（第一優先級）
        skill_setup = self._extract_skill_setup(root)
        
        # 提取裝備（第二優先級）
        equipment_snapshot = self._extract_equipment_snapshot(root)
        
        # 組裝標準化物件
        character = StandardizedCharacter(
            character_core=character_core,
            passive_allocation=passive_allocation,
            skill_setup=skill_setup,
            equipment_snapshot=equipment_snapshot,
            source="pob_import",
            pob_version=self.version_detected,
            import_timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"成功提取角色資料: {character_core.character_class} "
            f"Lv{character_core.level}"
        )
        
        return character
    
    def _extract_character_core(self, root: ET.Element) -> CharacterCore:
        """提取角色核心資訊"""
        build_elem = root.find("Build")
        
        if not build_elem:
            raise ValueError("找不到 Build 節點，PoB 資料可能損壞")
        
        # 基礎資訊
        level = int(build_elem.get("level", 1))
        character_class = build_elem.get("className", "Unknown")
        ascendancy = build_elem.get("ascendClassName", None)
        league = build_elem.get("league", "Standard")
        
        # 計算昇華狀態
        ascendancy_status, ascendancy_points = self._calculate_ascendancy_status(
            root,
            ascendancy
        )
        
        return CharacterCore(
            level=level,
            character_class=character_class,
            ascendancy=ascendancy,
            ascendancy_status=ascendancy_status,
            ascendancy_points=ascendancy_points,
            league=league
        )
    
    def _calculate_ascendancy_status(
        self,
        root: ET.Element,
        ascendancy_name: Optional[str]
    ) -> Tuple[AscendancyStatus, int]:
        """
        計算昇華完成度
        
        Returns:
            (昇華狀態, 已配置點數)
        """
        if not ascendancy_name:
            return AscendancyStatus.NONE, 0
        
        # 從天賦樹中計算昇華點數
        tree_elem = root.find("Tree")
        if not tree_elem:
            return AscendancyStatus.PARTIAL, 0
        
        spec_elem = tree_elem.find("Spec")
        if not spec_elem:
            return AscendancyStatus.PARTIAL, 0
        
        # 統計昇華節點
        ascendancy_nodes = 0
        for node_elem in spec_elem.findall("Node"):
            node_id = int(node_elem.get("nodeId", 0))
            # 昇華節點 ID 通常在特定範圍內（需要根據實際資料調整）
            # 這裡使用簡化邏輯，實際應查詢天賦樹資料庫
            if self._is_ascendancy_node(node_id):
                ascendancy_nodes += 1
        
        # 判斷完成度
        if ascendancy_nodes == 0:
            status = AscendancyStatus.NONE
        elif ascendancy_nodes < 8:
            status = AscendancyStatus.PARTIAL
        else:
            status = AscendancyStatus.COMPLETE
        
        return status, ascendancy_nodes
    
    def _is_ascendancy_node(self, node_id: int) -> bool:
        """
        判斷是否為昇華節點
        （簡化實作，實際應查詢天賦樹資料庫）
        """
        # 昇華節點通常在 60000+ 範圍
        return node_id >= 60000
    
    def _extract_passive_allocation(self, root: ET.Element) -> PassiveAllocation:
        """提取天賦樹配置"""
        tree_elem = root.find("Tree")
        
        if not tree_elem:
            logger.warning("找不到 Tree 節點，返回空天賦配置")
            return PassiveAllocation()
        
        spec_elem = tree_elem.find("Spec")
        if not spec_elem:
            logger.warning("找不到 Spec 節點，返回空天賦配置")
            return PassiveAllocation()
        
        # 提取已配置節點
        allocated_nodes = []
        for node_elem in spec_elem.findall("Node"):
            node_id = int(node_elem.get("nodeId", 0))
            if node_id > 0:
                allocated_nodes.append(node_id)
        
        # 提取天賦樹 URL
        url_elem = spec_elem.find("URL")
        tree_url = url_elem.text if url_elem is not None else None
        
        # 職業起始節點
        class_start = spec_elem.get("classId", None)
        class_start_node = int(class_start) if class_start else None
        
        # 這裡需要整合天賦樹服務來分類節點
        # 暫時返回基礎資料
        return PassiveAllocation(
            allocated_nodes=allocated_nodes,
            total_points_used=len(allocated_nodes),
            tree_url=tree_url,
            class_start_node=class_start_node
        )
    
    def _extract_skill_setup(self, root: ET.Element) -> SkillSetup:
        """提取技能配置"""
        skills_elem = root.find("Skills")
        
        if not skills_elem:
            logger.warning("找不到 Skills 節點，返回空技能配置")
            return SkillSetup()
        
        skill_groups = []
        main_skill_group = None
        
        # 獲取主技能組 ID
        build_elem = root.find("Build")
        main_socket_group = int(build_elem.get("mainSocketGroup", 1)) if build_elem else 1
        
        current_group_id = 1
        
        for skill_set in skills_elem.findall("SkillSet"):
            for skill in skill_set.findall("Skill"):
                enabled = skill.get("enabled", "true") == "true"
                label = skill.get("label", f"Group {current_group_id}")
                slot = skill.get("slot", "Unknown")
                
                # 提取寶石
                gems = []
                for gem_elem in skill.findall("Gem"):
                    gem_info = self._extract_gem_info(gem_elem)
                    gems.append(gem_info)
                
                # 計算連結數
                link_count = len([g for g in gems if g.enabled])
                
                # 識別主動技能
                main_skill = None
                support_gems = []
                
                for gem in gems:
                    if not gem.enabled:
                        continue
                    
                    if gem.is_support:
                        support_gems.append(gem.name)
                    else:
                        main_skill = gem.name
                
                # 建立技能組
                skill_group = SkillGroup(
                    label=label,
                    slot=slot,
                    enabled=enabled,
                    gems=gems,
                    link_count=link_count,
                    main_skill=main_skill,
                    support_gems=support_gems
                )
                
                skill_groups.append(skill_group)
                
                # 判斷是否為主技能組
                if current_group_id == main_socket_group and enabled:
                    main_skill_group = skill_group
                
                current_group_id += 1
        
        # 自動識別主技能組（如果未明確指定）
        if not main_skill_group and skill_groups:
            # 選擇連結數最多的技能組
            main_skill_group = max(
                (sg for sg in skill_groups if sg.main_skill),
                key=lambda sg: sg.link_count,
                default=None
            )
        
        return SkillSetup(
            skill_groups=skill_groups,
            main_skill_group=main_skill_group
        )
    
    def _extract_gem_info(self, gem_elem: ET.Element) -> GemInfo:
        """提取單個寶石資訊"""
        name = gem_elem.get("nameSpec", "Unknown")
        level = int(gem_elem.get("level", 1))
        quality = int(gem_elem.get("quality", 0))
        enabled = gem_elem.get("enabled", "true") == "true"

        # 提取 gemId（PoB 內部識別碼）
        gem_id = gem_elem.get("gemId", "")

        # 判斷寶石類型（優先使用 gemId）
        is_support = self._is_support_gem(name, gem_id)
        is_awakened = "Awakened" in name
        is_vaal = "Vaal" in name

        # 品質類型
        quality_id = gem_elem.get("qualityId", "Default")
        quality_type = self._parse_quality_type(quality_id)

        return GemInfo(
            name=name,
            level=level,
            quality=quality,
            quality_type=quality_type,
            is_support=is_support,
            is_awakened=is_awakened,
            is_vaal=is_vaal,
            enabled=enabled
        )
    
    def _is_support_gem(self, gem_name: str, gem_id: str = "") -> bool:
        """
        判斷是否為輔助寶石

        Args:
            gem_name: 寶石名稱
            gem_id: PoB 內部識別碼（備用）

        Returns:
            是否為輔助寶石
        """
        # 優先使用 RePoE 資料判斷（最可靠）
        gem_service = get_gem_service()
        if gem_service.is_support_gem(gem_name):
            return True

        # 備用：使用 gemId 判斷
        if gem_id and "SupportGem" in gem_id:
            return True

        # 最後備用：關鍵字比對（向後兼容）
        support_keywords = [
            "Support", "support",
            "Awakened", "awakened",
        ]
        return any(keyword in gem_name for keyword in support_keywords)
    
    def _parse_quality_type(self, quality_id: str) -> GemQualityType:
        """解析品質類型"""
        quality_map = {
            "Default": GemQualityType.DEFAULT,
            "Anomalous": GemQualityType.ANOMALOUS,
            "Divergent": GemQualityType.DIVERGENT,
            "Phantasmal": GemQualityType.PHANTASMAL
        }
        return quality_map.get(quality_id, GemQualityType.DEFAULT)
    
    def _extract_equipment_snapshot(self, root: ET.Element) -> EquipmentSnapshot:
        """提取裝備快照"""
        items_elem = root.find("Items")

        if not items_elem:
            logger.warning("找不到 Items 節點，返回空裝備配置")
            return EquipmentSnapshot()

        # PoB XML 結構：<Item id="N"> 與 <ItemSet> 是兄弟節點
        # <Slot> 用 itemId 屬性引用 <Item>，不是嵌套關係
        item_map = {}
        for item_elem in items_elem.findall("Item"):
            item_id = item_elem.get("id", "")
            if item_id:
                item_map[item_id] = item_elem

        equipment = {}

        # 裝備部位映射
        slot_mapping = {
            "Weapon 1": "weapon_main_hand",
            "Weapon 2": "weapon_off_hand",
            "Helmet": "helmet",
            "Body Armour": "body_armour",
            "Gloves": "gloves",
            "Boots": "boots",
            "Amulet": "amulet",
            "Ring 1": "ring_1",
            "Ring 2": "ring_2",
            "Belt": "belt",
            "Flask 1": "flask_1",
            "Flask 2": "flask_2",
            "Flask 3": "flask_3",
            "Flask 4": "flask_4",
            "Flask 5": "flask_5"
        }

        # 使用 activeItemSet 指定的 ItemSet，預設第一個
        active_set_id = items_elem.get("activeItemSet", "1")
        target_item_set = None
        for item_set in items_elem.findall("ItemSet"):
            if item_set.get("id", "") == active_set_id:
                target_item_set = item_set
                break
        if target_item_set is None:
            target_item_set = items_elem.find("ItemSet")
        if target_item_set is None:
            return EquipmentSnapshot()

        for slot_name, attr_name in slot_mapping.items():
            slot_elem = target_item_set.find(f"Slot[@name='{slot_name}']")
            if slot_elem is not None:
                item_id = slot_elem.get("itemId", "")
                if item_id and item_id in item_map:
                    equipment[attr_name] = self._extract_equipment_item(
                        item_map[item_id],
                        slot_name
                    )

        return EquipmentSnapshot(**equipment)

    def _extract_equipment_item(
        self,
        item_elem: ET.Element,
        slot: str
    ) -> EquipmentItem:
        """提取單件裝備資訊（從 PoB 物品文字解析，非 XML 屬性）"""
        item_text = item_elem.text if item_elem.text else ""
        name, rarity, item_level = self._parse_item_text_header(item_text)
        base_type = self._extract_base_type(item_text, name, rarity)

        return EquipmentItem(
            slot=slot,
            name=name,
            base_type=base_type,
            rarity=rarity,
            item_level=item_level
        )

    def _parse_item_text_header(self, item_text: str):
        """從 PoB 物品文字解析名稱、稀有度、物品等級"""
        lines = [ln.strip() for ln in item_text.strip().splitlines() if ln.strip()]
        rarity = ItemRarity.NORMAL
        item_level = 0

        for line in lines:
            if line.lower().startswith("rarity:"):
                rarity_str = line.split(":", 1)[1].strip().upper()
                rarity = ItemRarity[rarity_str] if rarity_str in ItemRarity.__members__ else ItemRarity.NORMAL
            elif line.lower().startswith("item level:"):
                try:
                    item_level = int(line.split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    pass

        # 名稱 = 過濾 "Rarity:" 後的第一行
        filtered = [ln for ln in lines if not ln.lower().startswith("rarity:")]
        name = filtered[0] if filtered else ""

        return name, rarity, item_level

    def _extract_base_type(self, item_text: str, name: str, rarity: "ItemRarity") -> str:
        """
        從 PoB 物品文字中解析基底類型。

        PoB item text 格式（clipboard copy 格式）：
          UNIQUE/RARE: 第一行=物品唯一名稱，第二行=基底類型
          NORMAL/MAGIC: 第一行=基底類型（名稱即基底）

        由於 name 已從 XML 屬性取得，文字第一行通常是 name 本身或基底類型。
        """
        if not item_text:
            return ""

        lines = [ln.strip() for ln in item_text.strip().splitlines() if ln.strip()]
        if not lines:
            return ""

        # 過濾掉 "Rarity: ..." 開頭的行
        filtered = [ln for ln in lines if not ln.lower().startswith("rarity:")]
        if not filtered:
            return ""

        is_named = rarity in (ItemRarity.UNIQUE, ItemRarity.RARE)

        if is_named and name:
            # UNIQUE/RARE：第一行是物品名（與 name 屬性相同），第二行是基底類型
            if filtered[0] == name and len(filtered) > 1:
                return filtered[1]
            # 若第一行不是 name，嘗試找 name 後的行
            for i, ln in enumerate(filtered):
                if ln == name and i + 1 < len(filtered):
                    return filtered[i + 1]
            # 找不到對應則回傳第一行
            return filtered[0]
        else:
            # NORMAL/MAGIC：第一行即基底類型
            return filtered[0]


# 導出便捷函數
def parse_pob_to_standard_character(
    pob_xml: str,
    lazy_load: bool = True
) -> StandardizedCharacter:
    """
    將 PoB XML 字串轉換為標準化角色物件
    
    Args:
        pob_xml: PoB XML 字串
        lazy_load: 是否使用惰性載入
        
    Returns:
        標準化角色物件
    """
    root = ET.fromstring(pob_xml)
    mapper = PobXmlMapper()
    return mapper.extract_standardized_character(root, lazy_load)