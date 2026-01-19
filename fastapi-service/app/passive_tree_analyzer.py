"""
天賦樹節點分類器與路徑分析引擎
"""
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from collections import deque
import logging

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """節點類型枚舉"""
    KEYSTONE = "keystone"  # 基石天賦
    NOTABLE = "notable"  # 顯著天賦
    JEWEL_SOCKET = "jewel_socket"  # 珠寶插槽
    MASTERY = "mastery"  # 精通
    ASCENDANCY = "ascendancy"  # 昇華節點
    SMALL_PASSIVE = "small_passive"  # 小型天賦
    CLASS_START = "class_start"  # 職業起始節點


class NodeWeight(int, Enum):
    """節點權重（用於優先級排序）"""
    KEYSTONE = 100
    NOTABLE = 50
    JEWEL_SOCKET = 30  # 基礎值，位置會調整
    MASTERY = 40
    ASCENDANCY = 80
    SMALL_PASSIVE = 1


class ClusterJewelSize(str, Enum):
    """星團珠寶大小"""
    SMALL = "small"  # 小型（2-3 天賦）
    MEDIUM = "medium"  # 中型（4-5 天賦）
    LARGE = "large"  # 大型（8-12 天賦）


class PassiveNode:
    """天賦節點資料結構"""
    
    def __init__(
        self,
        node_id: int,
        name: str,
        node_type: NodeType,
        stats: List[str],
        connections: List[int],
        is_cluster_socket: bool = False,
        cluster_size: Optional[ClusterJewelSize] = None
    ):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.stats = stats
        self.connections = connections
        self.is_cluster_socket = is_cluster_socket
        self.cluster_size = cluster_size
    
    @property
    def weight(self) -> int:
        """獲取節點權重"""
        base_weight = NodeWeight[self.node_type.upper()].value
        
        # 星團珠寶插槽根據大小調整權重
        if self.is_cluster_socket and self.cluster_size:
            if self.cluster_size == ClusterJewelSize.LARGE:
                return base_weight + 20
            elif self.cluster_size == ClusterJewelSize.MEDIUM:
                return base_weight + 10
        
        return base_weight


class PassiveTreeClassifier:
    """天賦樹節點分類器"""
    
    def __init__(self, passive_tree_data: Dict):
        """
        初始化分類器
        
        Args:
            passive_tree_data: 天賦樹 JSON 資料（來自官方 API）
        """
        self.tree_data = passive_tree_data
        self.node_map: Dict[int, PassiveNode] = {}
        self._build_node_map()
    
    def _build_node_map(self):
        """建立節點 ID -> PassiveNode 的映射"""
        if not self.tree_data or 'nodes' not in self.tree_data:
            logger.warning("天賦樹資料不完整")
            return
        
        for node_id_str, node_data in self.tree_data['nodes'].items():
            try:
                node_id = int(node_id_str)
                
                # 判斷節點類型
                node_type = self._classify_node_type(node_data)
                
                # 提取節點資訊
                name = node_data.get('name', node_data.get('dn', f'Node {node_id}'))
                stats = node_data.get('sd', node_data.get('stats', []))
                connections = node_data.get('out', [])
                
                # 判斷是否為星團珠寶插槽
                is_cluster = self._is_cluster_jewel_socket(node_data)
                cluster_size = self._determine_cluster_size(node_data) if is_cluster else None
                
                # 建立節點物件
                passive_node = PassiveNode(
                    node_id=node_id,
                    name=name,
                    node_type=node_type,
                    stats=stats,
                    connections=connections,
                    is_cluster_socket=is_cluster,
                    cluster_size=cluster_size
                )
                
                self.node_map[node_id] = passive_node
                
            except (ValueError, KeyError) as e:
                logger.warning(f"無法處理節點 {node_id_str}: {str(e)}")
                continue
        
        logger.info(f"成功建立 {len(self.node_map)} 個天賦節點映射")
    
    def _classify_node_type(self, node_data: Dict) -> NodeType:
        """
        分類節點類型
        
        Args:
            node_data: 節點資料
            
        Returns:
            節點類型
        """
        # 檢查是否為基石天賦
        if node_data.get('ks', node_data.get('isKeystone', False)):
            return NodeType.KEYSTONE
        
        # 檢查是否為顯著天賦
        if node_data.get('not', node_data.get('isNotable', False)):
            return NodeType.NOTABLE
        
        # 檢查是否為精通
        if node_data.get('m', node_data.get('isMastery', False)):
            return NodeType.MASTERY
        
        # 檢查是否為珠寶插槽
        if node_data.get('isJewelSocket', False):
            return NodeType.JEWEL_SOCKET
        
        # 檢查是否為昇華節點（通常 ID >= 60000）
        node_id = int(node_data.get('skill', 0))
        if node_id >= 60000:
            return NodeType.ASCENDANCY
        
        # 預設為小型天賦
        return NodeType.SMALL_PASSIVE
    
    def _is_cluster_jewel_socket(self, node_data: Dict) -> bool:
        """判斷是否為星團珠寶插槽"""
        # 星團珠寶插槽通常有特殊標記或在特定區域
        # 這需要根據實際資料結構調整
        expansion_jewel = node_data.get('expansionJewel', {})
        return bool(expansion_jewel)
    
    def _determine_cluster_size(self, node_data: Dict) -> Optional[ClusterJewelSize]:
        """判斷星團珠寶大小"""
        expansion_jewel = node_data.get('expansionJewel', {})
        if not expansion_jewel:
            return None
        
        # 根據星團珠寶的節點數判斷大小
        total_indices = expansion_jewel.get('totalIndices', 0)
        
        if total_indices <= 3:
            return ClusterJewelSize.SMALL
        elif total_indices <= 6:
            return ClusterJewelSize.MEDIUM
        else:
            return ClusterJewelSize.LARGE
    
    def get_node(self, node_id: int) -> Optional[PassiveNode]:
        """獲取節點資訊"""
        return self.node_map.get(node_id)
    
    def classify_nodes(self, node_ids: List[int]) -> Dict[NodeType, List[int]]:
        """
        將節點 ID 列表分類
        
        Args:
            node_ids: 節點 ID 列表
            
        Returns:
            按類型分類的節點字典
        """
        classified = {
            NodeType.KEYSTONE: [],
            NodeType.NOTABLE: [],
            NodeType.JEWEL_SOCKET: [],
            NodeType.MASTERY: [],
            NodeType.ASCENDANCY: [],
            NodeType.SMALL_PASSIVE: []
        }
        
        for node_id in node_ids:
            node = self.get_node(node_id)
            if node:
                classified[node.node_type].append(node_id)
        
        return classified


class PassiveTreePathFinder:
    """天賦樹路徑追蹤引擎"""
    
    def __init__(self, classifier: PassiveTreeClassifier):
        """
        初始化路徑追蹤器
        
        Args:
            classifier: 節點分類器
        """
        self.classifier = classifier
    
    def find_shortest_path(
        self,
        start_nodes: List[int],
        target_node: int,
        allocated_nodes: Set[int]
    ) -> Optional[Dict]:
        """
        使用 BFS 尋找最短路徑
        
        Args:
            start_nodes: 起始節點列表（已配置的節點）
            target_node: 目標節點
            allocated_nodes: 已配置節點集合
            
        Returns:
            路徑資訊字典，包含路徑、成本、效益比
        """
        if target_node in allocated_nodes:
            return {
                "found": True,
                "path": [],
                "cost": 0,
                "already_allocated": True
            }
        
        # 從所有起始節點開始 BFS
        queue = deque()
        visited = set(allocated_nodes)
        parent_map = {}
        
        # 初始化佇列
        for start in start_nodes:
            if start in allocated_nodes:
                queue.append(start)
                visited.add(start)
        
        # BFS 搜尋
        while queue:
            current = queue.popleft()
            
            # 獲取當前節點
            current_node = self.classifier.get_node(current)
            if not current_node:
                continue
            
            # 檢查所有連接的節點
            for neighbor in current_node.connections:
                if neighbor == target_node:
                    # 找到目標，重建路徑
                    path = self._reconstruct_path(parent_map, current, neighbor)
                    return self._analyze_path(path, allocated_nodes)
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent_map[neighbor] = current
                    queue.append(neighbor)
        
        # 找不到路徑
        return {
            "found": False,
            "message": "無法從已配置節點到達目標節點"
        }
    
    def _reconstruct_path(
        self,
        parent_map: Dict[int, int],
        last_node: int,
        target_node: int
    ) -> List[int]:
        """重建路徑"""
        path = [target_node]
        current = last_node
        
        while current in parent_map:
            path.append(current)
            current = parent_map[current]
        
        path.reverse()
        return path
    
    def _analyze_path(
        self,
        path: List[int],
        allocated_nodes: Set[int]
    ) -> Dict:
        """
        分析路徑效益
        
        Args:
            path: 路徑節點列表
            allocated_nodes: 已配置節點
            
        Returns:
            路徑分析結果
        """
        # 移除已配置的節點
        new_nodes = [n for n in path if n not in allocated_nodes]
        
        # 計算總權重
        total_weight = 0
        detour_nodes = []  # 繞路節點（低價值節點）
        valuable_nodes = []  # 高價值節點
        
        for node_id in new_nodes:
            node = self.classifier.get_node(node_id)
            if node:
                total_weight += node.weight
                
                # 判斷是否為繞路節點
                if node.node_type == NodeType.SMALL_PASSIVE and len(node.stats) == 0:
                    detour_nodes.append(node_id)
                elif node.weight >= NodeWeight.NOTABLE.value:
                    valuable_nodes.append(node_id)
        
        # 計算效益比
        cost = len(new_nodes)
        efficiency = total_weight / cost if cost > 0 else 0
        
        return {
            "found": True,
            "path": new_nodes,
            "cost": cost,
            "total_weight": total_weight,
            "efficiency": efficiency,
            "detour_nodes": detour_nodes,
            "valuable_nodes": valuable_nodes,
            "node_details": [
                {
                    "id": node_id,
                    "name": self.classifier.get_node(node_id).name,
                    "type": self.classifier.get_node(node_id).node_type.value,
                    "weight": self.classifier.get_node(node_id).weight
                }
                for node_id in new_nodes
                if self.classifier.get_node(node_id)
            ]
        }
    
    def suggest_optimal_paths(
        self,
        allocated_nodes: Set[int],
        missing_keystones: List[int],
        missing_notables: List[int],
        max_suggestions: int = 5
    ) -> List[Dict]:
        """
        建議最佳天賦路徑
        
        Args:
            allocated_nodes: 已配置節點
            missing_keystones: 缺少的基石天賦
            missing_notables: 缺少的顯著天賦
            max_suggestions: 最大建議數量
            
        Returns:
            建議列表（按效益比排序）
        """
        suggestions = []
        
        # 優先處理基石天賦
        priority_targets = [
            (node_id, "keystone") for node_id in missing_keystones
        ] + [
            (node_id, "notable") for node_id in missing_notables
        ]
        
        for target_id, node_category in priority_targets[:max_suggestions * 2]:
            path_result = self.find_shortest_path(
                list(allocated_nodes),
                target_id,
                allocated_nodes
            )
            
            if path_result.get("found") and not path_result.get("already_allocated"):
                target_node = self.classifier.get_node(target_id)
                
                suggestions.append({
                    "target_node_id": target_id,
                    "target_node_name": target_node.name if target_node else "Unknown",
                    "category": node_category,
                    "path": path_result["path"],
                    "cost": path_result["cost"],
                    "efficiency": path_result["efficiency"],
                    "detour_count": len(path_result.get("detour_nodes", [])),
                    "priority": 10 if node_category == "keystone" else 5
                })
        
        # 按效益比排序
        suggestions.sort(key=lambda x: (-x["priority"], x["cost"], -x["efficiency"]))
        
        return suggestions[:max_suggestions]


class ClusterJewelAnalyzer:
    """星團珠寶分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.cluster_jewel_database = self._build_cluster_database()
    
    def _build_cluster_database(self) -> Dict[str, Dict]:
        """建立星團珠寶類型資料庫"""
        return {
            ClusterJewelSize.SMALL.value: {
                "max_passives": 3,
                "notable_count": 1,
                "point_cost_range": (2, 3)
            },
            ClusterJewelSize.MEDIUM.value: {
                "max_passives": 6,
                "notable_count": 2,
                "point_cost_range": (4, 6)
            },
            ClusterJewelSize.LARGE.value: {
                "max_passives": 12,
                "notable_count": 3,
                "point_cost_range": (8, 12)
            }
        }
    
    def analyze_cluster_jewel(
        self,
        jewel_data: Dict,
        target_build_type: str
    ) -> Dict:
        """
        分析星團珠寶匹配度
        
        Args:
            jewel_data: 珠寶資料
            target_build_type: 目標流派類型
            
        Returns:
            匹配度分析結果
        """
        jewel_size = jewel_data.get("size", ClusterJewelSize.MEDIUM.value)
        enchants = jewel_data.get("enchants", [])
        notables = jewel_data.get("notables", [])
        
        # 獲取珠寶規格
        spec = self.cluster_jewel_database.get(jewel_size, {})
        
        # 計算點數成本
        passive_count = jewel_data.get("passives", spec.get("max_passives", 6))
        
        return {
            "size": jewel_size,
            "passive_count": passive_count,
            "point_cost": passive_count,
            "notables": notables,
            "enchants": enchants,
            "match_score": self._calculate_match_score(
                enchants,
                notables,
                target_build_type
            ),
            "recommendations": self._generate_cluster_recommendations(
                jewel_size,
                enchants,
                notables,
                target_build_type
            )
        }
    
    def _calculate_match_score(
        self,
        enchants: List[str],
        notables: List[str],
        build_type: str
    ) -> float:
        """
        計算匹配度分數（0-100）
        
        這裡需要建立流派與詞綴的對應關係資料庫
        簡化版本先返回基礎分數
        """
        # TODO: 實作詞綴匹配邏輯
        base_score = 50.0
        
        if enchants:
            base_score += 10.0
        
        if notables:
            base_score += len(notables) * 10.0
        
        return min(base_score, 100.0)
    
    def _generate_cluster_recommendations(
        self,
        size: str,
        enchants: List[str],
        notables: List[str],
        build_type: str
    ) -> List[str]:
        """生成星團珠寶改進建議"""
        recommendations = []
        
        if not enchants:
            recommendations.append(f"建議添加 {size} 星團珠寶的附魔詞綴")
        
        spec = self.cluster_jewel_database.get(size, {})
        expected_notables = spec.get("notable_count", 2)
        
        if len(notables) < expected_notables:
            recommendations.append(
                f"建議增加顯著天賦數量（目前 {len(notables)}，建議 {expected_notables}）"
            )
        
        return recommendations