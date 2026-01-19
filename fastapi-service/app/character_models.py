"""
標準化角色資料模型
將 PoB XML 資料轉換為統一的內部格式
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class AscendancyStatus(str, Enum):
    """昇華狀態枚舉"""
    NONE = "none"  # 未昇華
    PARTIAL = "partial"  # 部分昇華（1-7 點）
    COMPLETE = "complete"  # 完整昇華（8 點）


class GemQualityType(str, Enum):
    """寶石品質類型"""
    DEFAULT = "Default"
    ANOMALOUS = "Anomalous"  # 異常
    DIVERGENT = "Divergent"  # 分歧
    PHANTASMAL = "Phantasmal"  # 幻影


class ItemRarity(str, Enum):
    """物品稀有度"""
    NORMAL = "NORMAL"
    MAGIC = "MAGIC"
    RARE = "RARE"
    UNIQUE = "UNIQUE"


class SocketColor(str, Enum):
    """插槽顏色"""
    RED = "R"  # 力量
    GREEN = "G"  # 敏捷
    BLUE = "B"  # 智慧
    WHITE = "W"  # 通用


# ===== 核心角色資訊 =====

class CharacterCore(BaseModel):
    """角色核心資訊"""
    level: int = Field(..., ge=1, le=100, description="角色等級")
    character_class: str = Field(..., description="職業名稱")
    ascendancy: Optional[str] = Field(None, description="昇華職業名稱")
    ascendancy_status: AscendancyStatus = Field(
        default=AscendancyStatus.NONE,
        description="昇華完成度"
    )
    ascendancy_points: int = Field(
        default=0,
        ge=0,
        le=8,
        description="已配置的昇華點數"
    )
    league: str = Field(default="Standard", description="賽季名稱")
    
    # 計算屬性
    @property
    def available_passive_points(self) -> int:
        """計算可用天賦點數（不含任務獎勵）"""
        return self.level - 1
    
    @property
    def total_available_points(self) -> int:
        """計算總可用點數（包含任務獎勵 22 點）"""
        return self.level - 1 + 22


# ===== 天賦樹配置 =====

class JewelSocketInfo(BaseModel):
    """珠寶插槽資訊"""
    node_id: int = Field(..., description="節點 ID")
    socket_type: str = Field(
        default="regular",
        description="插槽類型: regular, cluster_small, cluster_medium, cluster_large"
    )
    is_allocated: bool = Field(default=False, description="是否已配置")
    jewel_equipped: Optional[Dict[str, Any]] = Field(
        None,
        description="已裝備的珠寶資訊"
    )


class PassiveAllocation(BaseModel):
    """天賦樹配置資訊"""
    allocated_nodes: List[int] = Field(
        default_factory=list,
        description="已配置節點 ID 列表"
    )
    total_points_used: int = Field(default=0, description="已使用天賦點數")
    
    # 分類節點
    keystone_nodes: List[int] = Field(
        default_factory=list,
        description="基石天賦節點 ID"
    )
    notable_nodes: List[int] = Field(
        default_factory=list,
        description="顯著天賦節點 ID"
    )
    jewel_sockets: List[JewelSocketInfo] = Field(
        default_factory=list,
        description="珠寶插槽列表"
    )
    cluster_jewel_sockets: List[JewelSocketInfo] = Field(
        default_factory=list,
        description="星團珠寶插槽列表"
    )
    
    # 天賦樹 URL（用於視覺化）
    tree_url: Optional[str] = Field(None, description="天賦樹 URL")
    class_start_node: Optional[int] = Field(None, description="職業起始節點 ID")


# ===== 寶石配置 =====

class GemInfo(BaseModel):
    """寶石詳細資訊"""
    name: str = Field(..., description="寶石名稱")
    level: int = Field(default=1, ge=1, le=50, description="寶石等級（包含裝備加成）")
    quality: int = Field(default=0, ge=0, le=50, description="寶石品質（包含裝備加成）")
    quality_type: GemQualityType = Field(
        default=GemQualityType.DEFAULT,
        description="品質類型"
    )
    is_support: bool = Field(default=False, description="是否為輔助寶石")
    is_awakened: bool = Field(default=False, description="是否為覺醒寶石")
    is_vaal: bool = Field(default=False, description="是否為瓦爾寶石")
    enabled: bool = Field(default=True, description="是否啟用")
    
    # 額外資訊
    experience_percent: Optional[float] = Field(
        None,
        description="經驗值百分比"
    )


class SkillGroup(BaseModel):
    """技能組資訊"""
    label: str = Field(..., description="技能組標籤")
    slot: str = Field(..., description="裝備插槽位置")
    enabled: bool = Field(default=True, description="是否啟用")
    
    # 寶石列表
    gems: List[GemInfo] = Field(default_factory=list, description="寶石列表")
    
    # 連結資訊
    link_count: int = Field(default=0, description="實際連結數")
    
    # 分類資訊
    main_skill: Optional[str] = Field(None, description="主動技能名稱")
    support_gems: List[str] = Field(
        default_factory=list,
        description="輔助寶石名稱列表"
    )
    
    @property
    def is_main_skill_group(self) -> bool:
        """判斷是否為主技能組（有主動技能且連結數 >= 4）"""
        return self.main_skill is not None and self.link_count >= 4


class SkillSetup(BaseModel):
    """技能配置總覽"""
    skill_groups: List[SkillGroup] = Field(
        default_factory=list,
        description="所有技能組"
    )
    
    # 分類技能組
    main_skill_group: Optional[SkillGroup] = Field(
        None,
        description="主技能組"
    )
    aura_groups: List[SkillGroup] = Field(
        default_factory=list,
        description="光環技能組列表"
    )
    utility_groups: List[SkillGroup] = Field(
        default_factory=list,
        description="輔助技能組列表"
    )
    
    @property
    def main_link_count(self) -> int:
        """獲取主技能組連結數"""
        if self.main_skill_group:
            return self.main_skill_group.link_count
        return 0


# ===== 裝備配置 =====

class SocketGroup(BaseModel):
    """插槽組資訊"""
    colors: List[SocketColor] = Field(
        default_factory=list,
        description="插槽顏色列表"
    )
    linked: bool = Field(default=False, description="是否連結")


class ItemModifier(BaseModel):
    """物品詞綴"""
    text: str = Field(..., description="詞綴文字")
    mod_type: str = Field(
        ...,
        description="詞綴類型: implicit, explicit, crafted, fractured, synthesised, enchant"
    )
    tier: Optional[int] = Field(None, description="詞綴層級 (T1-T7)")
    value_ranges: Optional[Dict[str, float]] = Field(
        None,
        description="數值範圍"
    )


class EquipmentItem(BaseModel):
    """裝備物品詳細資訊"""
    slot: str = Field(..., description="裝備部位")
    name: str = Field(default="", description="物品名稱")
    base_type: str = Field(default="", description="基底類型")
    rarity: ItemRarity = Field(default=ItemRarity.NORMAL, description="稀有度")
    
    # 物品屬性
    item_level: int = Field(default=0, description="物品等級")
    quality: int = Field(default=0, description="品質")
    sockets: List[SocketGroup] = Field(
        default_factory=list,
        description="插槽組列表"
    )
    
    # 詞綴
    implicit_mods: List[ItemModifier] = Field(
        default_factory=list,
        description="固有詞綴"
    )
    explicit_mods: List[ItemModifier] = Field(
        default_factory=list,
        description="明文詞綴"
    )
    crafted_mods: List[ItemModifier] = Field(
        default_factory=list,
        description="工藝詞綴"
    )
    fractured_mods: List[ItemModifier] = Field(
        default_factory=list,
        description="固化詞綴"
    )
    enchant_mods: List[ItemModifier] = Field(
        default_factory=list,
        description="附魔詞綴"
    )
    
    # 特殊標記
    is_corrupted: bool = Field(default=False, description="是否汙染")
    is_mirrored: bool = Field(default=False, description="是否鏡像")
    is_synthesised: bool = Field(default=False, description="是否追憶")
    is_elder: bool = Field(default=False, description="是否尊師物品")
    is_shaper: bool = Field(default=False, description="是否塑者物品")
    is_crusader: bool = Field(default=False, description="是否聖戰軍物品")
    is_hunter: bool = Field(default=False, description="是否狩獵者物品")
    is_redeemer: bool = Field(default=False, description="是否救贖者物品")
    is_warlord: bool = Field(default=False, description="是否督軍物品")
    
    @property
    def total_sockets(self) -> int:
        """總插槽數"""
        return sum(len(group.colors) for group in self.sockets)
    
    @property
    def max_links(self) -> int:
        """最大連結數"""
        return max(
            (len(group.colors) for group in self.sockets if group.linked),
            default=0
        )


class EquipmentSnapshot(BaseModel):
    """裝備快照總覽"""
    # 主要裝備部位
    weapon_main_hand: Optional[EquipmentItem] = Field(None, description="主手武器")
    weapon_off_hand: Optional[EquipmentItem] = Field(None, description="副手武器/盾牌")
    helmet: Optional[EquipmentItem] = Field(None, description="頭盔")
    body_armour: Optional[EquipmentItem] = Field(None, description="胸甲")
    gloves: Optional[EquipmentItem] = Field(None, description="手套")
    boots: Optional[EquipmentItem] = Field(None, description="鞋子")
    amulet: Optional[EquipmentItem] = Field(None, description="項鍊")
    ring_1: Optional[EquipmentItem] = Field(None, description="戒指 1")
    ring_2: Optional[EquipmentItem] = Field(None, description="戒指 2")
    belt: Optional[EquipmentItem] = Field(None, description="腰帶")
    
    # 藥劑
    flask_1: Optional[EquipmentItem] = Field(None, description="藥劑 1")
    flask_2: Optional[EquipmentItem] = Field(None, description="藥劑 2")
    flask_3: Optional[EquipmentItem] = Field(None, description="藥劑 3")
    flask_4: Optional[EquipmentItem] = Field(None, description="藥劑 4")
    flask_5: Optional[EquipmentItem] = Field(None, description="藥劑 5")
    
    # 珠寶（天賦樹上的）
    jewels: List[EquipmentItem] = Field(
        default_factory=list,
        description="珠寶列表"
    )
    
    def get_item_by_slot(self, slot: str) -> Optional[EquipmentItem]:
        """根據部位名稱獲取裝備"""
        slot_mapping = {
            "mainhand": self.weapon_main_hand,
            "offhand": self.weapon_off_hand,
            "helmet": self.helmet,
            "body": self.body_armour,
            "gloves": self.gloves,
            "boots": self.boots,
            "amulet": self.amulet,
            "ring1": self.ring_1,
            "ring2": self.ring_2,
            "belt": self.belt,
            "flask1": self.flask_1,
            "flask2": self.flask_2,
            "flask3": self.flask_3,
            "flask4": self.flask_4,
            "flask5": self.flask_5,
        }
        return slot_mapping.get(slot.lower())


# ===== 完整角色模型 =====

class StandardizedCharacter(BaseModel):
    """標準化角色模型（內部統一格式）"""
    character_core: CharacterCore = Field(..., description="核心角色資訊")
    passive_allocation: PassiveAllocation = Field(
        default_factory=PassiveAllocation,
        description="天賦樹配置"
    )
    skill_setup: SkillSetup = Field(
        default_factory=SkillSetup,
        description="技能配置"
    )
    equipment_snapshot: EquipmentSnapshot = Field(
        default_factory=EquipmentSnapshot,
        description="裝備快照"
    )
    
    # 元資料
    source: str = Field(default="pob_import", description="資料來源")
    pob_version: Optional[str] = Field(None, description="PoB 版本")
    import_timestamp: Optional[str] = Field(None, description="匯入時間戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "character_core": {
                    "level": 95,
                    "character_class": "Ranger",
                    "ascendancy": "Deadeye",
                    "ascendancy_status": "complete",
                    "ascendancy_points": 8
                },
                "passive_allocation": {
                    "allocated_nodes": [1234, 5678],
                    "total_points_used": 117
                },
                "skill_setup": {
                    "main_link_count": 6
                },
                "source": "pob_import"
            }
        }