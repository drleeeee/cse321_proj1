# src/bstar_tree.py

class BStarNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.rids = []
        self.children = []

    def find_index(self, key):
        """이진 탐색을 통한 인덱스 탐색 (O(log d))"""
        left, right = 0, len(self.keys) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.keys[mid] < key:
                left = mid + 1
            else:
                right = mid - 1
        return left

class BStarTree:
    def __init__(self, order):
        if order < 3: 
            raise ValueError("B*-tree order must be at least 3.")
        self.order = order
        self.max_keys = order - 1
        self.min_keys = (2 * order - 1) // 3 
        self.root = BStarNode(is_leaf=True)
        self.split_count = 0        
        self.redistribute_count = 0 

    # ==========================================
    # SEARCH LOGIC
    # ==========================================
    def search(self, key):
        return self._search_node(self.root, key)

    def _search_node(self, node, key):
        i = node.find_index(key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.rids[i]
        if node.is_leaf:
            return None
        return self._search_node(node.children[i], key)

    # ==========================================
    # INSERT LOGIC (Fully Robust Architecture)
    # ==========================================
    def insert(self, key, rid):
        """삽입 후 루트 노드가 오버플로우 상태인지 확인하고 1-to-2 분할 수행"""
        self._insert_recursive(self.root, key, rid)
        
        if len(self.root.keys) > self.max_keys:
            self.split_count += 1
            new_root = BStarNode(is_leaf=False)
            new_root.children.append(self.root)
            self._split_root_1_to_2(new_root, 0)
            self.root = new_root

    def _insert_recursive(self, node, key, rid):
        i = node.find_index(key)

        # 1. 중복 키 업데이트
        if i < len(node.keys) and node.keys[i] == key:
            node.rids[i] = rid
            return

        # 2. 리프 노드에 도달한 경우 데이터 삽입
        if node.is_leaf:
            node.keys.insert(i, key)
            node.rids.insert(i, rid)
        else:
            # 3. 내부 노드인 경우 자식으로 재귀 호출
            self._insert_recursive(node.children[i], key, rid)
            
            # 재귀 호출 복귀 후, 방금 다녀온 자식 노드의 오버플로우 여부 검사
            if len(node.children[i].keys) > self.max_keys:
                self._handle_overflow(node, i)

    def _handle_overflow(self, parent, i):
        """자식 노드(children[i])의 오버플로우를 해결합니다."""
        # 1. 왼쪽 형제와 재분배 시도
        if i > 0 and len(parent.children[i-1].keys) < self.max_keys:
            self.redistribute_count += 1
            self._shift_to_left(parent, i)
            return

        # 2. 오른쪽 형제와 재분배 시도
        if i < len(parent.children) - 1 and len(parent.children[i+1].keys) < self.max_keys:
            self.redistribute_count += 1
            self._shift_to_right(parent, i)
            return

        # 3. 양쪽 형제 모두 가득 찼다면 2-to-3 분할 수행
        self.split_count += 1
        if i < len(parent.children) - 1:
            self._split_2_to_3(parent, i)
        else:
            self._split_2_to_3(parent, i - 1)

    def _shift_to_left(self, parent, i):
        """children[i]의 첫 번째 요소를 children[i-1]로 이동"""
        left = parent.children[i-1]
        child = parent.children[i]
        
        left.keys.append(parent.keys[i-1])
        left.rids.append(parent.rids[i-1])
        if not child.is_leaf:
            left.children.append(child.children.pop(0))
            
        parent.keys[i-1] = child.keys.pop(0)
        parent.rids[i-1] = child.rids.pop(0)

    def _shift_to_right(self, parent, i):
        """children[i]의 마지막 요소를 children[i+1]로 이동"""
        child = parent.children[i]
        right = parent.children[i+1]
        
        right.keys.insert(0, parent.keys[i])
        right.rids.insert(0, parent.rids[i])
        if not child.is_leaf:
            right.children.insert(0, child.children.pop())
            
        parent.keys[i] = child.keys.pop()
        parent.rids[i] = child.rids.pop()

    def _split_2_to_3(self, parent, i):
        """children[i]와 children[i+1] 두 노드를 세 개의 노드로 분할"""
        left = parent.children[i]
        right = parent.children[i+1]
        
        all_keys = left.keys + [parent.keys[i]] + right.keys
        all_rids = left.rids + [parent.rids[i]] + right.rids
        all_children = (left.children + right.children) if not left.is_leaf else []
        
        total = len(all_keys)
        m1 = total // 3
        m2 = (2 * total) // 3
        
        mid = BStarNode(is_leaf=left.is_leaf)
        
        # 3개의 노드로 데이터 분배
        left.keys, left.rids = all_keys[:m1], all_rids[:m1]
        mid.keys, mid.rids = all_keys[m1+1:m2], all_rids[m1+1:m2]
        right.keys, right.rids = all_keys[m2+1:], all_rids[m2+1:]
        
        if not left.is_leaf:
            left.children = all_children[:m1+1]
            mid.children = all_children[m1+1:m2+1]
            right.children = all_children[m2+1:]
            
        # 부모 노드 갱신
        parent.keys[i] = all_keys[m1]
        parent.rids[i] = all_rids[m1]
        
        parent.keys.insert(i+1, all_keys[m2])
        parent.rids.insert(i+1, all_rids[m2])
        parent.children.insert(i+1, mid)

    def _split_root_1_to_2(self, parent, i):
        """루트 노드 전용 B-tree 스타일 1-to-2 분할"""
        child = parent.children[i]
        mid_idx = len(child.keys) // 2
        
        new_node = BStarNode(is_leaf=child.is_leaf)
        new_node.keys = child.keys[mid_idx+1:]
        new_node.rids = child.rids[mid_idx+1:]
        if not child.is_leaf:
            new_node.children = child.children[mid_idx+1:]
            child.children = child.children[:mid_idx+1]
            
        parent.keys.insert(i, child.keys[mid_idx])
        parent.rids.insert(i, child.rids[mid_idx])
        parent.children.insert(i+1, new_node)
        
        child.keys = child.keys[:mid_idx]
        child.rids = child.rids[:mid_idx]

# ==========================================
    # DELETE LOGIC (Bottom-Up Architecture)
    # ==========================================
    def delete(self, key):
        if not self.root.keys:
            return False
        self._delete_recursive(self.root, None, 0, key)
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]

    def _delete_recursive(self, node, parent, parent_idx, key):
        i = node.find_index(key)
        
        # 1. 키를 찾은 경우
        if i < len(node.keys) and node.keys[i] == key:
            if node.is_leaf:
                node.keys.pop(i)
                node.rids.pop(i)
            else:
                sk, sr = self._get_successor(node, i)
                node.keys[i] = sk
                node.rids[i] = sr
                self._delete_recursive(node.children[i+1], node, i+1, sk)
        # 2. 키를 찾지 못한 경우 자식으로 이동
        else:
            if node.is_leaf:
                return
            self._delete_recursive(node.children[i], node, i, key)

        # 3. [핵심] 재귀가 풀려 올라오면서 Underflow(최소 키 개수 미만) 체크 및 복구
        if parent and len(node.keys) < self.min_keys:
            self._handle_underflow(node, parent, parent_idx)

    def _get_successor(self, node, index):
        curr = node.children[index+1]
        while not curr.is_leaf:
            curr = curr.children[0]
        return curr.keys[0], curr.rids[0]

    def _handle_underflow(self, node, parent, i):
        # 1. 왼쪽 형제에게서 빌려오기
        if i > 0 and len(parent.children[i-1].keys) > self.min_keys:
            left = parent.children[i-1]
            node.keys.insert(0, parent.keys[i-1])
            node.rids.insert(0, parent.rids[i-1])
            parent.keys[i-1] = left.keys.pop()
            parent.rids[i-1] = left.rids.pop()
            if not node.is_leaf:
                node.children.insert(0, left.children.pop())
            return
            
        # 2. 오른쪽 형제에게서 빌려오기
        if i < len(parent.children) - 1 and len(parent.children[i+1].keys) > self.min_keys:
            right = parent.children[i+1]
            node.keys.append(parent.keys[i])
            node.rids.append(parent.rids[i])
            parent.keys[i] = right.keys.pop(0)
            parent.rids[i] = right.rids.pop(0)
            if not node.is_leaf:
                node.children.append(right.children.pop(0))
            return

        # 3. 빌려올 수 없다면 형제와 병합 (Merge)
        if i > 0:
            self._merge(parent, i-1)
        else:
            self._merge(parent, i)

    def _merge(self, parent, i):
        left = parent.children[i]
        right = parent.children[i+1]

        # 부모의 구분 키를 왼쪽 자식으로 내림
        left.keys.append(parent.keys.pop(i))
        left.rids.append(parent.rids.pop(i))
        
        # 오른쪽 자식의 모든 데이터를 왼쪽 자식에 합침
        left.keys.extend(right.keys)
        left.rids.extend(right.rids)
        if not left.is_leaf:
            left.children.extend(right.children)
            
        # 불필요해진 오른쪽 자식 포인터 제거
        parent.children.pop(i+1)