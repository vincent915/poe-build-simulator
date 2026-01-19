"""
整合比對引擎
整合天賦樹分析與裝備寶石分析功能
"""
from typing import List, Dict, Any
import logging

from app.character_models import StandardizedCharacter
from app.priority_comparison_engine import (
    ComparisonPriority,
    DifferenceCategory,
    ComparisonDifference,
    PriorityComparisonEngine
)
from app.passive_tree_analyzer import (
    PassiveTreeClassifier,
    PassiveTreePathFinder,
    ClusterJewelAnalyzer
)
from app.equipment_gem_analyzer import (
    EquipmentAnalyzer,
    GemCombinationAnalyzer,
    LinkEvaluator
)

logger = logging.getLogger(__name__)


class EnhancedComparisonEngine(PriorityComparisonEngine):
    """增強版比對引擎（整合深度分析）"""
    
    def __init__(
        self,
        passive_tree_data: Dict = None,
        enable_advanced_analysis: bool = True
    ):
        """
        初始化增強版引擎
        
        Args:
            passive_tree_data: 天賦樹 JSON 資料
            enable_advanced_analysis: 是否啟用進階分析
        """
        super().__init__()
        
        self.enable_advanced = enable_advanced_analysis
        
        # 初始化分析器
        if passive_tree_data and enable_advanced_analysis:
            self.tree_classifier = PassiveTreeClassifier(passive_tree_data)
            self.tree_pathfinder = PassiveTreePathFinder(self.tree_classifier)
        else:
            self.tree_classifier = None
            self.tree_pathfinder = None
        
        self.cluster_analyzer = ClusterJewelAnalyzer()
        self.equipment_analyzer = EquipmentAnalyzer()
        self.gem_analyzer = GemCombinationAnalyzer()
        self.link_evaluator = LinkEvaluator()
    
    def compare_characters(
        self,
        player_character: StandardizedCharacter,
        target_character: StandardizedCharacter
    ) -> List[ComparisonDifference]:
        """
        執行完整角色比對（含進階分析）
        
        Args:
            player_character: 玩家角色
            target_character: 目標角色
            
        Returns:
            差異列表
        """
        # 執行基礎比對
        logger.info("執行基礎三層優先級比對")
        self.differences = super().compare_characters(player_character, target_character)
        
        if not self.enable_advanced:
            logger.info("進階分析已停用，返回基礎比對結果")
            return self.differences
        
        # 執行進階分析
        logger.info("執行進階深度分析")
        
        # 天賦樹深度分析
        if self.tree_classifier and self.tree_pathfinder:
            self._advanced_passive_analysis(player_character, target_character)
        
        # 裝備深度分析
        self._advanced_equipment_analysis(player_character, target_character)
        
        # 寶石組合深度分析
        self._advanced_gem_analysis(player_character, target_character)
        
        # 重新排序
        self._sort_by_priority()
        
        logger.info(f"增強比對完成，共 {len(self.differences)} 項差異")
        
        return self.differences
    
    def _advanced_passive_analysis(
        self,
        player: StandardizedCharacter,
        target: StandardizedCharacter
    ):
        """天賦樹深度分析"""
        logger.info("開始天賦樹深度分析")
        
        player_nodes = set(player.passive_allocation.allocated_nodes)
        target_nodes = set(target.passive_allocation.allocated_nodes)
        
        # 分類節點
        target_classified = self.tree_classifier.classify_nodes(
            list(target_nodes)
        )
        player_classified = self.tree_classifier.classify_nodes(
            list(player_nodes)
        )
        
        # 分析缺失的基石天賦
        missing_keystones = list(
            set(target_classified["keystone"]) - set(player_classified["keystone"])
        )
        
        # 分析缺失的顯著天賦
        missing_notables = list(
            set(target_classified["notable"]) - set(player_classified["notable"])
        )
        
        if missing_keystones or missing_notables:
            # 使用路徑追蹤器建議最佳路徑
            path_suggestions = self.tree_pathfinder.suggest_optimal_paths(
                player_nodes,
                missing_keystones,
                missing_notables,
                max_suggestions=3
            )
            
            for suggestion in path_suggestions:
                self.differences.append(ComparisonDifference(
                    category=DifferenceCategory.PASSIVE_KEYSTONE
                    if suggestion["category"] == "keystone"
                    else DifferenceCategory.PASSIVE_NOTABLE,
                    priority=ComparisonPriority.HIGH,
                    message=f"建議配置天賦：{suggestion['target_node_name']}",
                    current_value=None,
                    target_value=suggestion["target_node_id"],
                    action=f"需投資 {suggestion['cost']} 個天賦點",
                    pob_instruction=(
                        f"在 PoB 的天賦樹中配置 {suggestion['target_node_name']}，"
                        f"建議路徑經過 {suggestion['cost']} 個節點"
                    ),
                    path_details={
                        "path_nodes": suggestion["path"],
                        "efficiency": suggestion["efficiency"],
                        "detour_count": suggestion.get("detour_count", 0)
                    }
                ))
        
        # 分析星團珠寶
        self._analyze_cluster_jewels(player, target)
    
    def _analyze_cluster_jewels(
        self,
        player: StandardizedCharacter,
        target: StandardizedCharacter
    ):
        """分析星團珠寶配置"""
        logger.info("分析星團珠寶配置")
        
        # 這裡需要從裝備快照中提取星團珠寶資訊
        # 簡化版本先跳過
        pass
    
    def _advanced_equipment_analysis(
        self,
        player: StandardizedCharacter,
        target: StandardizedCharacter
    ):
        """裝備深度分析"""
        logger.info("開始裝備深度分析")
        
        # 核心裝備部位
        core_slots = ["weapon_main_hand", "body_armour"]
        
        for slot in core_slots:
            player_item = player.equipment_snapshot.get_item_by_slot(slot)
            target_item = target.equipment_snapshot.get_item_by_slot(slot)
            
            if not target_item or not player_item:
                continue
            
            # 基底層級比對
            base_comparison = self.equipment_analyzer.compare_equipment_base(
                player_item.dict() if hasattr(player_item, 'dict') else player_item,
                target_item.dict() if hasattr(target_item, 'dict') else target_item
            )
            
            if base_comparison["has_differences"]:
                for diff in base_comparison["differences"]:
                    self.differences.append(ComparisonDifference(
                        category=DifferenceCategory.EQUIPMENT_CORE,
                        priority=self._map_severity_to_priority(diff["severity"]),
                        message=diff["message"],
                        current_value=diff["current"],
                        target_value=diff["target"],
                        action=f"改善 {slot} 的{diff['type']}",
                        pob_instruction=f"在 PoB 中調整 {slot} 的屬性",
                        impact=diff.get("impact", ""),
                        slot=slot
                    ))
            
            # 詞綴分析
            player_mods = (player_item.explicit_mods + player_item.implicit_mods
                          if hasattr(player_item, 'explicit_mods') else [])
            target_mods = (target_item.explicit_mods + target_item.implicit_mods
                          if hasattr(target_item, 'explicit_mods') else [])
            
            mod_analysis = self.equipment_analyzer.analyze_mod_gap(
                [{"text": m.text} for m in player_mods] if player_mods else [],
                [{"text": m.text} for m in target_mods] if target_mods else []
            )
            
            if mod_analysis["missing_count"] > 0:
                self.differences.append(ComparisonDifference(
                    category=DifferenceCategory.EQUIPMENT_MODS,
                    priority=ComparisonPriority.MEDIUM,
                    message=f"{slot} 缺少 {mod_analysis['missing_count']} 個關鍵詞綴",
                    current_value=None,
                    target_value=mod_analysis["missing_mods"],
                    action=f"為 {slot} 添加詞綴：{', '.join(mod_analysis['missing_mods'][:3])}",
                    pob_instruction=f"在 PoB 中為 {slot} 添加這些詞綴以查看效果",
                    slot=slot,
                    recommendations=mod_analysis["recommendations"]
                ))
    
    def _advanced_gem_analysis(
        self,
        player: StandardizedCharacter,
        target: StandardizedCharacter
    ):
        """寶石組合深度分析"""
        logger.info("開始寶石組合深度分析")
        
        player_main = player.skill_setup.main_skill_group
        target_main = target.skill_setup.main_skill_group
        
        if not player_main or not target_main:
            return
        
        # 轉換為字典格式
        player_gems = [
            {
                "name": g.name,
                "level": g.level,
                "quality": g.quality,
                "is_support": g.is_support,
                "is_awakened": g.is_awakened,
                "enabled": g.enabled,
                "quality_type": g.quality_type.value
            }
            for g in player_main.gems
        ]
        
        target_gems = [
            {
                "name": g.name,
                "level": g.level,
                "quality": g.quality,
                "is_support": g.is_support,
                "is_awakened": g.is_awakened,
                "enabled": g.enabled,
                "quality_type": g.quality_type.value
            }
            for g in target_main.gems
        ]
        
        # 深度分析
        gem_analysis = self.gem_analyzer.analyze_gem_combination(
            player_gems,
            target_gems
        )
        
        # 倍率差距分析
        multiplier_gap = gem_analysis["multiplier_comparison"]["gap_percentage"]
        
        if multiplier_gap > 5:  # 倍率差距超過 5%
            self.differences.append(ComparisonDifference(
                category=DifferenceCategory.GEM_MISSING,
                priority=ComparisonPriority.HIGH,
                message=f"寶石組合倍率差距：{multiplier_gap:.1f}%",
                current_value=gem_analysis["multiplier_comparison"]["player"],
                target_value=gem_analysis["multiplier_comparison"]["target"],
                action="優化輔助寶石組合以提升倍率",
                pob_instruction="調整輔助寶石配置並觀察 DPS 變化",
                multiplier_details=gem_analysis["multiplier_comparison"]
            ))
        
        # 覺醒寶石升級建議
        awakened_upgrades = gem_analysis["support_gem_analysis"].get("awakened_upgrades", [])
        
        for upgrade in awakened_upgrades:
            self.differences.append(ComparisonDifference(
                category=DifferenceCategory.GEM_MISSING,
                priority=ComparisonPriority.MEDIUM,
                message=f"可升級為覺醒寶石：{upgrade['current']}",
                current_value=upgrade["current"],
                target_value=upgrade["upgrade_to"],
                action=f"將 {upgrade['current']} 升級為 {upgrade['upgrade_to']}",
                pob_instruction=f"在 PoB 中替換為覺醒版本",
                expected_gain=f"預計提升 {upgrade['multiplier_gain']*100:.0f}% 倍率"
            ))
        
        # 連結數評估
        link_evaluation = self.link_evaluator.evaluate_link_requirement(
            player_main.link_count,
            target_main.link_count,
            "RARE"  # 簡化：假設為稀有裝備
        )
        
        if not link_evaluation["satisfied"]:
            self.differences.append(ComparisonDifference(
                category=DifferenceCategory.SKILL_LINKS,
                priority=ComparisonPriority.CRITICAL,
                message=f"主技能連結不足：{link_evaluation['current_links']}L → {link_evaluation['target_links']}L",
                current_value=link_evaluation["current_links"],
                target_value=link_evaluation["target_links"],
                action=f"獲得 {link_evaluation['target_links']} 連裝備",
                pob_instruction="在 PoB 中確保主技能裝備有足夠連結",
                difficulty=link_evaluation["difficulty"],
                estimated_cost=link_evaluation["estimated_cost"],
                recommendations=link_evaluation["recommendations"]
            ))
    
    def _map_severity_to_priority(self, severity: str) -> ComparisonPriority:
        """將嚴重度映射為優先級"""
        mapping = {
            "critical": ComparisonPriority.CRITICAL,
            "high": ComparisonPriority.HIGH,
            "medium": ComparisonPriority.MEDIUM,
            "low": ComparisonPriority.LOW
        }
        return mapping.get(severity, ComparisonPriority.MEDIUM)