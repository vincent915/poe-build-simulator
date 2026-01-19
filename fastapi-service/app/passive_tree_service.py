import requests
from functools import lru_cache
from typing import Dict, List, Optional
import logging
from collections import deque

logger = logging.getLogger(__name__)

class PassiveTreeService:
    def __init__(self):
        self.tree_data = None
        self.node_map = {}
        self.loaded = False
        
    @lru_cache(maxsize=1)
    def load_tree_data(self) -> bool:
        """載入 POE 官方天賦樹資料（只載入一次，快取結果）"""
        if self.loaded and self.node_map:
            logger.info("天賦樹資料已載入，使用快取")
            return True
            
        try:
            # POE 官方 GitHub repository (永遠最新版本)
            url = "https://raw.githubusercontent.com/grindinggear/skilltree-export/master/data.json"
            logger.info(f"正在載入天賦樹資料: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            self.tree_data = response.json()
            logger.info(f"成功取得天賦樹 JSON，大小: {len(response.content)} bytes")
            
            # 建立節點 ID -> 節點資訊的映射
            if 'nodes' in self.tree_data:
                for node_id_str, node_info in self.tree_data['nodes'].items():
                    try:
                        node_id = int(node_id_str)
                        
                        # 判斷節點類型（支援新舊兩種欄位名稱）
                        is_keystone = node_info.get('ks', node_info.get('isKeystone', False))
                        is_notable = node_info.get('not', node_info.get('isNotable', False))
                        is_mastery = node_info.get('m', node_info.get('isMastery', False))
                        is_jewel = node_info.get('isJewelSocket', False)
                        
                        node_type = 'normal'
                        if is_keystone:
                            node_type = 'keystone'
                        elif is_notable:
                            node_type = 'notable'
                        elif is_mastery:
                            node_type = 'mastery'
                        elif is_jewel:
                            node_type = 'jewel_socket'
                        
                        # 取得節點名稱和效果（支援新舊兩種欄位名稱）
                        name = node_info.get('name', node_info.get('dn', f'Node {node_id}'))
                        stats = node_info.get('sd', node_info.get('stats', []))
                        
                        self.node_map[node_id] = {
                            'id': node_id,
                            'name': name,
                            'stats': stats,
                            'type': node_type,
                            'isKeystone': is_keystone,
                            'isNotable': is_notable,
                            'isMastery': is_mastery,
                            'isJewelSocket': is_jewel,
                            'icon': node_info.get('icon', ''),
                            'flavourText': node_info.get('flavourText', []),
                            'out': node_info.get('out', [])  # 連接的節點
                        }
                    except (ValueError, KeyError) as e:
                        logger.warning(f"無法處理節點 {node_id_str}: {str(e)}")
                        continue
                
                self.loaded = True
                logger.info(f"✅ 成功載入 {len(self.node_map)} 個天賦節點資料")
                return True
            else:
                logger.error("天賦樹資料格式錯誤：找不到 'nodes' 欄位")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("載入天賦樹資料超時")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"網路請求失敗: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"載入天賦樹資料失敗: {str(e)}")
            return False
    
    def get_node_info(self, node_id: int) -> Dict:
        """取得單一節點資訊"""
        if not self.loaded:
            self.load_tree_data()
        
        return self.node_map.get(node_id, {
            'id': node_id,
            'name': f'Unknown Node {node_id}',
            'stats': [],
            'type': 'unknown',
            'isKeystone': False,
            'isNotable': False,
            'isMastery': False,
            'isJewelSocket': False,
            'icon': '',
            'flavourText': [],
            'out': []
        })
    
    def get_nodes_info(self, node_ids: List[int]) -> Dict[int, Dict]:
        """批次取得多個節點資訊"""
        if not self.loaded:
            self.load_tree_data()
        
        result = {}
        for node_id in node_ids:
            result[node_id] = self.get_node_info(node_id)
        
        return result
    
    def get_node_name(self, node_id: int) -> str:
        """快速取得節點名稱"""
        info = self.get_node_info(node_id)
        return info.get('name', f'Node {node_id}')
    
    def is_loaded(self) -> bool:
        """檢查資料是否已載入"""
        return self.loaded and len(self.node_map) > 0
    
    def _build_node_graph(self) -> Dict[int, List[int]]:
        """建立節點連接圖"""
        graph = {}
        
        for node_id, node_info in self.node_map.items():
            # 獲取連接的節點
            connected = node_info.get('out', [])
            graph[node_id] = connected
        
        return graph
    
    def _bfs_shortest_path(self, graph: Dict[int, List[int]], start: int, target: int) -> Optional[List[int]]:
        """使用 BFS 找最短路徑"""
        if start == target:
            return [start]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            # 檢查當前節點的所有鄰居
            for neighbor in graph.get(current, []):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # 找不到路徑
    
    def calculate_path(self, start_nodes: List[int], target_node: int) -> Dict:
        """計算從已點節點到目標節點的最短路徑"""
        if not self.loaded:
            self.load_tree_data()
        
        # 建立節點連接圖
        graph = self._build_node_graph()
        
        # 使用 BFS 找最短路徑
        shortest_path = None
        min_distance = float('inf')
        
        for start_node in start_nodes:
            path = self._bfs_shortest_path(graph, start_node, target_node)
            if path and len(path) < min_distance:
                shortest_path = path
                min_distance = len(path)
        
        if not shortest_path:
            return {
                'found': False,
                'message': '找不到路徑'
            }
        
        # 移除起點（已經點了）
        path_nodes = shortest_path[1:] if len(shortest_path) > 1 else []
        
        return {
            'found': True,
            'path': path_nodes,
            'cost': len(path_nodes),
            'nodes_info': [self.get_node_info(nid) for nid in path_nodes]
        }
    
    def suggest_optimal_paths(self, allocated_nodes: List[int], missing_nodes: List[int], max_suggestions: int = 5) -> List[Dict]:
        """建議最佳天賦路徑"""
        if not self.loaded:
            self.load_tree_data()
        
        suggestions = []
        
        # 只處理關鍵節點（基石和顯著天賦）
        priority_nodes = []
        for node_id in missing_nodes:
            node_info = self.get_node_info(node_id)
            if node_info.get('isKeystone') or node_info.get('isNotable'):
                priority_nodes.append({
                    'id': node_id,
                    'info': node_info,
                    'priority': 10 if node_info.get('isKeystone') else 5
                })
        
        # 按優先級排序
        priority_nodes.sort(key=lambda x: x['priority'], reverse=True)
        
        # 計算每個關鍵節點的路徑
        for node_data in priority_nodes[:max_suggestions]:
            node_id = node_data['id']
            path_result = self.calculate_path(allocated_nodes, node_id)
            
            if path_result['found']:
                suggestions.append({
                    'target_node': node_id,
                    'target_info': node_data['info'],
                    'path': path_result['path'],
                    'cost': path_result['cost'],
                    'priority': node_data['priority'],
                    'nodes_on_path': path_result['nodes_info']
                })
        
        # 按成本排序（成本低的優先）
        suggestions.sort(key=lambda x: (x['cost'], -x['priority']))
        
        return suggestions

# 全域單例
passive_tree_service = PassiveTreeService()