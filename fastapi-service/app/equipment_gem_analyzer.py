"""
裝備與寶石深度分析引擎
"""
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class ModTier(int, Enum):
    """詞綴層級"""
    T1 = 1
    T2 = 2
    T3 = 3
    T4 = 4
    T5 = 5
    T6 = 6
    T7 = 7
    UNKNOWN = 99


class ModType(str, Enum):
    """詞綴類型"""
    PREFIX = "prefix"
    SUFFIX = "suffix"
    IMPLICIT = "implicit"
    CRAFTED = "crafted"
    FRACTURED = "fractured"
    SYNTHESISED = "synthesised"
    ENCHANT = "enchant"


class GemMultiplierType(str, Enum):
    """寶石倍率類型"""
    MORE = "more"  # 乘算
    INCREASED = "increased"  # 加算


class EquipmentAnalyzer:
    """裝備深度分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.mod_database = self._build_mod_database()
        self.base_type_database = self._build_base_type_database()
    
    def _build_mod_database(self) -> Dict:
        """建立詞綴資料庫（簡化版）"""
        return {
            # 生命詞綴
            "life": {
                "T1": {"min": 80, "max": 89, "prefix": True},
                "T2": {"min": 70, "max": 79, "prefix": True},
                "T3": {"min": 60, "max": 69, "prefix": True},
            },
            # 抗性詞綴
            "resistance": {
                "T1": {"min": 46, "max": 48, "suffix": True},
                "T2": {"min": 42, "max": 45, "suffix": True},
                "T3": {"min": 36, "max": 41, "suffix": True},
            },
            # 物理傷害詞綴
            "physical_damage": {
                "T1": {"min": 170, "max": 179, "prefix": True},
                "T2": {"min": 150, "max": 169, "prefix": True},
            }
        }
    
    def _build_base_type_database(self) -> Dict:
        """建立基底類型資料庫"""
        return {
            "weapons": {
                "wand": ["Imbued Wand", "Opal Wand", "Prophecy Wand", "Convoking Wand"],
                "bow": ["Thicket Bow", "Short Bow", "Recurve Bow"],
                "claw": ["Gemini Claw", "Imperial Claw", "Terror Claw"]
            },
            "armour": {
                "body_armour": ["Astral Plate", "Glorious Plate", "Vaal Regalia"],
                "helmet": ["Royal Burgonet", "Hubris Circlet", "Bone Helmet"],
                "gloves": ["Spiked Gloves", "Fingerless Silk Gloves", "Gripped Gloves"],
                "boots": ["Two-Toned Boots", "Sorcerer Boots", "Murder Boots"]
            }
        }
    
    def compare_equipment_base(
        self,
        player_item: Dict,
        target_item: Dict
    ) -> Dict:
        """
        比對裝備基底層級
        
        Args:
            player_item: 玩家裝備
            target_item: 目標裝備
            
        Returns:
            基底比對結果
        """
        differences = []
        
        # 物品等級檢查
        player_ilvl = player_item.get("item_level", 0)
        target_ilvl = target_item.get("item_level", 0)
        
        if player_ilvl < target_ilvl:
            differences.append({
                "type": "item_level",
                "severity": "high" if target_ilvl >= 86 else "medium",
                "current": player_ilvl,
                "target": target_ilvl,
                "message": f"物品等級過低：iLv{player_ilvl} → iLv{target_ilvl}",
                "impact": "限制可詞綴的最高層級詞綴"
            })
        
        # 基底類型檢查
        player_base = player_item.get("base_type", "")
        target_base = target_item.get("base_type", "")
        
        if player_base != target_base:
            differences.append({
                "type": "base_type",
                "severity": "critical",
                "current": player_base,
                "target": target_base,
                "message": f"基底類型不符：{player_base} → {target_base}",
                "impact": "基底屬性差異會影響整體強度"
            })
        
        # 品質檢查
        player_quality = player_item.get("quality", 0)
        target_quality = target_item.get("quality", 0)
        
        if player_quality < target_quality:
            differences.append({
                "type": "quality",
                "severity": "low",
                "current": player_quality,
                "target": target_quality,
                "message": f"品質不足：{player_quality}% → {target_quality}%",
                "impact": "影響防禦值或武器傷害"
            })
        
        return {
            "has_differences": len(differences) > 0,
            "differences": differences,
            "compatibility_score": self._calculate_base_compatibility(
                player_item,
                target_item
            )
        }
    
    def _calculate_base_compatibility(
        self,
        player_item: Dict,
        target_item: Dict
    ) -> float:
        """計算基底相容性分數（0-100）"""
        score = 100.0
        
        # 基底類型不同扣 50 分
        if player_item.get("base_type") != target_item.get("base_type"):
            score -= 50.0
        
        # 物品等級差距扣分
        ilvl_diff = target_item.get("item_level", 0) - player_item.get("item_level", 0)
        if ilvl_diff > 0:
            score -= min(ilvl_diff * 2, 30.0)
        
        # 品質差距扣分
        quality_diff = target_item.get("quality", 0) - player_item.get("quality", 0)
        if quality_diff > 0:
            score -= min(quality_diff * 0.5, 10.0)
        
        return max(score, 0.0)
    
    def analyze_mod_gap(
        self,
        player_mods: List[Dict],
        target_mods: List[Dict]
    ) -> Dict:
        """
        分析詞綴缺口
        
        Args:
            player_mods: 玩家詞綴列表
            target_mods: 目標詞綴列表
            
        Returns:
            詞綴缺口分析
        """
        # 提取關鍵詞
        player_keywords = self._extract_mod_keywords(player_mods)
        target_keywords = self._extract_mod_keywords(target_mods)
        
        # 計算缺失的關鍵詞
        missing_keywords = target_keywords - player_keywords
        
        # 計算額外的關鍵詞（可能衝突）
        extra_keywords = player_keywords - target_keywords
        
        # 分析詞綴層級差異
        tier_differences = self._compare_mod_tiers(player_mods, target_mods)
        
        return {
            "missing_mods": list(missing_keywords),
            "missing_count": len(missing_keywords),
            "conflicting_mods": list(extra_keywords),
            "tier_differences": tier_differences,
            "recommendations": self._generate_mod_recommendations(
                missing_keywords,
                tier_differences
            )
        }
    
    def _extract_mod_keywords(self, mods: List[Dict]) -> Set[str]:
        """提取詞綴關鍵詞"""
        keywords = set()
        
        important_keywords = [
            "Life", "Energy Shield", "Mana",
            "Resistance", "Elemental Resistance",
            "Chaos Resistance",
            "Increased Damage", "Added Physical Damage",
            "Added Cold Damage", "Added Fire Damage", "Added Lightning Damage",
            "Critical Strike", "Attack Speed", "Cast Speed",
            "+# to Level of"
        ]
        
        for mod in mods:
            mod_text = mod.get("text", "")
            
            for keyword in important_keywords:
                if keyword.lower() in mod_text.lower():
                    keywords.add(keyword)
        
        return keywords
    
    def _compare_mod_tiers(
        self,
        player_mods: List[Dict],
        target_mods: List[Dict]
    ) -> List[Dict]:
        """比對詞綴層級"""
        tier_diffs = []
        
        # 簡化版：只比對關鍵詞匹配的詞綴
        for target_mod in target_mods:
            target_text = target_mod.get("text", "")
            target_tier = target_mod.get("tier", ModTier.UNKNOWN.value)
            
            # 在玩家詞綴中尋找相似詞綴
            for player_mod in player_mods:
                player_text = player_mod.get("text", "")
                
                if self._mods_are_similar(player_text, target_text):
                    player_tier = player_mod.get("tier", ModTier.UNKNOWN.value)
                    
                    if player_tier > target_tier:  # 數字越小層級越高
                        tier_diffs.append({
                            "mod_type": self._identify_mod_category(target_text),
                            "player_tier": f"T{player_tier}",
                            "target_tier": f"T{target_tier}",
                            "message": f"詞綴層級較低：{player_text}"
                        })
        
        return tier_diffs
    
    def _mods_are_similar(self, mod1: str, mod2: str) -> bool:
        """判斷兩個詞綴是否相似（簡化版）"""
        # 提取關鍵詞比對
        keywords1 = set(re.findall(r'\b[A-Z][a-z]+\b', mod1))
        keywords2 = set(re.findall(r'\b[A-Z][a-z]+\b', mod2))
        
        # 如果有 50% 以上的關鍵詞重疊，視為相似
        if not keywords1 or not keywords2:
            return False
        
        overlap = len(keywords1 & keywords2)
        total = len(keywords1 | keywords2)
        
        return overlap / total >= 0.5
    
    def _identify_mod_category(self, mod_text: str) -> str:
        """識別詞綴類別"""
        categories = {
            "life": ["Life"],
            "resistance": ["Resistance"],
            "damage": ["Damage", "Added"],
            "critical": ["Critical"],
            "speed": ["Speed"]
        }
        
        for category, keywords in categories.items():
            if any(kw in mod_text for kw in keywords):
                return category
        
        return "other"
    
    def _generate_mod_recommendations(
        self,
        missing_keywords: Set[str],
        tier_differences: List[Dict]
    ) -> List[str]:
        """生成詞綴改進建議"""
        recommendations = []
        
        if missing_keywords:
            recommendations.append(
                f"需要添加以下詞綴：{', '.join(list(missing_keywords)[:3])}"
            )
        
        if tier_differences:
            recommendations.append(
                f"有 {len(tier_differences)} 個詞綴層級需要提升"
            )
        
        return recommendations


class GemCombinationAnalyzer:
    """寶石組合分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.support_multipliers = self._build_support_multiplier_database()
    
    def _build_support_multiplier_database(self) -> Dict:
        """建立輔助寶石倍率資料庫"""
        return {
            # More 倍率（乘算）
            "more": {
                "Awakened Added Cold Damage Support": 1.49,
                "Added Cold Damage Support": 1.44,
                "Elemental Damage with Attacks Support": 1.54,
                "Awakened Elemental Damage with Attacks Support": 1.59,
                "Vicious Projectiles Support": 1.49,
                "Hypothermia Support": 1.39,
                "Inspiration Support": 1.39,
                "Trinity Support": 1.49,
                "Multistrike Support": 1.44,
                "Melee Physical Damage Support": 1.49,
            },
            # Increased 倍率（加算）
            "increased": {
                "Increased Critical Strikes Support": 1.35,
                "Increased Critical Damage Support": 1.38,
            }
        }
    
    def analyze_gem_combination(
        self,
        player_gems: List[Dict],
        target_gems: List[Dict]
    ) -> Dict:
        """
        分析寶石組合差異
        
        Args:
            player_gems: 玩家寶石列表
            target_gems: 目標寶石列表
            
        Returns:
            組合分析結果
        """
        # 分離主動技能與輔助寶石
        player_active = [g for g in player_gems if not g.get("is_support")]
        player_supports = [g for g in player_gems if g.get("is_support")]
        
        target_active = [g for g in target_gems if not g.get("is_support")]
        target_supports = [g for g in target_gems if g.get("is_support")]
        
        # 比對主動技能
        active_comparison = self._compare_active_gems(player_active, target_active)
        
        # 比對輔助寶石
        support_comparison = self._compare_support_gems(player_supports, target_supports)
        
        # 計算總倍率
        player_multiplier = self._calculate_total_multiplier(player_supports)
        target_multiplier = self._calculate_total_multiplier(target_supports)
        
        return {
            "active_gem_analysis": active_comparison,
            "support_gem_analysis": support_comparison,
            "multiplier_comparison": {
                "player": player_multiplier,
                "target": target_multiplier,
                "gap": target_multiplier - player_multiplier,
                "gap_percentage": ((target_multiplier - player_multiplier) / player_multiplier * 100)
                if player_multiplier > 0 else 0
            },
            "optimization_score": self._calculate_gem_optimization_score(
                player_gems,
                target_gems
            )
        }
    
    def _compare_active_gems(
        self,
        player_active: List[Dict],
        target_active: List[Dict]
    ) -> Dict:
        """比對主動技能"""
        if not player_active or not target_active:
            return {"status": "missing_data"}
        
        player_gem = player_active[0]
        target_gem = target_active[0]
        
        differences = []
        
        # 檢查寶石名稱
        if player_gem.get("name") != target_gem.get("name"):
            differences.append({
                "type": "different_skill",
                "severity": "critical",
                "current": player_gem.get("name"),
                "target": target_gem.get("name")
            })
        
        # 檢查等級
        level_gap = target_gem.get("level", 1) - player_gem.get("level", 1)
        if level_gap > 0:
            differences.append({
                "type": "level_gap",
                "severity": "high" if level_gap >= 3 else "medium",
                "gap": level_gap,
                "current": player_gem.get("level"),
                "target": target_gem.get("level")
            })
        
        # 檢查品質
        quality_gap = target_gem.get("quality", 0) - player_gem.get("quality", 0)
        if quality_gap > 0:
            differences.append({
                "type": "quality_gap",
                "severity": "medium",
                "gap": quality_gap,
                "current": player_gem.get("quality"),
                "target": target_gem.get("quality")
            })
        
        # 檢查品質類型
        if player_gem.get("quality_type") != target_gem.get("quality_type"):
            differences.append({
                "type": "quality_type",
                "severity": "low",
                "current": player_gem.get("quality_type"),
                "target": target_gem.get("quality_type")
            })
        
        return {
            "has_differences": len(differences) > 0,
            "differences": differences
        }
    
    def _compare_support_gems(
        self,
        player_supports: List[Dict],
        target_supports: List[Dict]
    ) -> Dict:
        """比對輔助寶石"""
        player_names = {g.get("name") for g in player_supports}
        target_names = {g.get("name") for g in target_supports}
        
        missing_supports = target_names - player_names
        extra_supports = player_names - target_names
        
        # 檢查覺醒寶石替代
        awakened_upgrades = self._identify_awakened_upgrades(
            player_supports,
            target_supports
        )
        
        return {
            "missing_supports": list(missing_supports),
            "extra_supports": list(extra_supports),
            "awakened_upgrades": awakened_upgrades,
            "match_rate": len(player_names & target_names) / len(target_names) * 100
            if target_names else 100
        }
    
    def _identify_awakened_upgrades(
        self,
        player_supports: List[Dict],
        target_supports: List[Dict]
    ) -> List[Dict]:
        """識別覺醒寶石升級機會"""
        upgrades = []
        
        for target_gem in target_supports:
            if not target_gem.get("is_awakened"):
                continue
            
            # 找到對應的普通版本
            base_name = target_gem.get("name", "").replace("Awakened ", "")
            
            for player_gem in player_supports:
                if player_gem.get("name") == base_name:
                    upgrades.append({
                        "current": base_name,
                        "upgrade_to": target_gem.get("name"),
                        "multiplier_gain": 0.05  # 覺醒寶石通常提升 5% 倍率
                    })
        
        return upgrades
    
    def _calculate_total_multiplier(self, support_gems: List[Dict]) -> float:
        """計算總倍率"""
        more_multiplier = 1.0
        increased_total = 0.0
        
        for gem in support_gems:
            if not gem.get("enabled", True):
                continue
            
            gem_name = gem.get("name", "")
            
            # 查詢 More 倍率
            if gem_name in self.support_multipliers["more"]:
                more_multiplier *= self.support_multipliers["more"][gem_name]
            
            # 查詢 Increased 倍率
            if gem_name in self.support_multipliers["increased"]:
                increased_total += (self.support_multipliers["increased"][gem_name] - 1.0)
        
        # 總倍率 = More 倍率 × (1 + Increased 總和)
        total = more_multiplier * (1.0 + increased_total)
        
        return round(total, 2)
    
    def _calculate_gem_optimization_score(
        self,
        player_gems: List[Dict],
        target_gems: List[Dict]
    ) -> float:
        """計算寶石優化分數（0-100）"""
        score = 100.0
        
        player_names = {g.get("name") for g in player_gems}
        target_names = {g.get("name") for g in target_gems}
        
        # 缺少寶石扣分
        missing_count = len(target_names - player_names)
        score -= missing_count * 15
        
        # 等級品質差距扣分（簡化）
        for target_gem in target_gems:
            target_name = target_gem.get("name")
            player_gem = next(
                (g for g in player_gems if g.get("name") == target_name),
                None
            )
            
            if player_gem:
                level_gap = target_gem.get("level", 1) - player_gem.get("level", 1)
                score -= max(level_gap * 2, 0)
                
                quality_gap = target_gem.get("quality", 0) - player_gem.get("quality", 0)
                score -= max(quality_gap * 0.5, 0)
        
        return max(score, 0.0)


class LinkEvaluator:
    """連結數評估器"""
    
    def evaluate_link_requirement(
        self,
        current_links: int,
        target_links: int,
        item_rarity: str
    ) -> Dict:
        """
        評估連結數需求
        
        Args:
            current_links: 當前連結數
            target_links: 目標連結數
            item_rarity: 物品稀有度
            
        Returns:
            評估結果
        """
        if current_links >= target_links:
            return {
                "satisfied": True,
                "message": "連結數已滿足需求"
            }
        
        link_gap = target_links - current_links
        
        # 評估達成難度
        difficulty = self._assess_link_difficulty(target_links, item_rarity)
        
        # 計算預估成本
        estimated_cost = self._estimate_linking_cost(target_links, item_rarity)
        
        # 提供建議
        recommendations = self._generate_link_recommendations(
            current_links,
            target_links,
            difficulty
        )
        
        return {
            "satisfied": False,
            "current_links": current_links,
            "target_links": target_links,
            "link_gap": link_gap,
            "difficulty": difficulty,
            "estimated_cost": estimated_cost,
            "recommendations": recommendations
        }
    
    def _assess_link_difficulty(self, target_links: int, rarity: str) -> str:
        """評估達成難度"""
        if target_links <= 4:
            return "easy"
        elif target_links == 5:
            return "medium" if rarity == "RARE" else "hard"
        elif target_links == 6:
            return "very_hard" if rarity == "RARE" else "extremely_hard"
        else:
            return "impossible"
    
    def _estimate_linking_cost(self, target_links: int, rarity: str) -> Dict:
        """預估連結成本（通貨數量）"""
        # 簡化的成本估算
        costs = {
            4: {"fusings": 10, "jewellers": 20},
            5: {"fusings": 150, "jewellers": 50},
            6: {"fusings": 1500, "jewellers": 100}
        }
        
        return costs.get(target_links, {"fusings": 0, "jewellers": 0})
    
    def _generate_link_recommendations(
        self,
        current: int,
        target: int,
        difficulty: str
    ) -> List[str]:
        """生成連結建議"""
        recommendations = []
        
        if target == 6 and current < 4:
            recommendations.append(
                "建議先使用 Tabula Rasa（6 白連）作為過渡裝備"
            )
        
        if difficulty in ["very_hard", "extremely_hard"]:
            recommendations.append(
                "考慮購買已連結的基底，或使用工藝台強制 6 連（1500 個鏈結石）"
            )
        
        recommendations.append(
            f"使用連結石與工匠石嘗試達成 {target} 連"
        )
        
        return recommendations