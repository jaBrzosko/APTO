from spanning import SpanningNode, SpanningTree
from vertex import Vertex
from table import Table


class RootedNode:
    def __init__(self, data, u: Vertex, v: Vertex, isFace = False):
        self.data = data
        self.u = u
        self.v = v
        self.isFace = isFace
        self.parent = None
        self.children = []
        self.lb = None
        self.rb = None
        self.enclosingFaceRoot = None
        self.enclosedComponents = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def add_child_at(self, child, index):
        self.children.insert(index, child)
        child.parent = self

    def first_child(self):
        return self.children[0] if len(self.children) > 0 else None

    def last_child_vertex(self):
        return self.children[-1].v if len(self.children) > 0 else self.v

    def swap_uv(self):
        self.u, self.v = self.v, self.u

    def vertex_in(self, u):
        return self.u.id == u.id or self.v.id == u.id
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def add_subtree(self, subRoot):
        u = subRoot.u
        for i, child in enumerate(self.children):
            if child.v == u:
                self.add_child_at(subRoot, i + 1)
                return True
        for child in self.children:
            if len(child.children) > 0:
                if child.add_subtree(subRoot):
                    return True
        return False
    
    def reverse(self):
        self.u, self.v = self.v, self.u
        self.children.reverse()
        for child in self.children:
            child.reverse()

    def find_face_root(self, face):
        if self.isFace and self.data.id == face.id:
            return self
        for child in self.children:
            possibleFace = child.find_face_root(face)
            if possibleFace is not None:
                return possibleFace
        return None

    def add_encloser(self, faceRoot):
        if not self.isFace:
            return
        self.enclosingFaceRoot = faceRoot
        for child in self.children:
            child.add_encloser(faceRoot)

    def add_enclosed_component(self, component):
        self.enclosedComponents.append(component)
        component.rootedTree.root.add_encloser(self)

    def get_leaves(self):
        if self.is_leaf():
            return [self]
        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())
        return leaves
    
    def finalize_lbrb(self):
        if not self.isFace:
            return
        for child in self.children:
            child.finalize_lbrb()
        self.lb = self.children[0].lb
        self.rb = self.children[-1].rb

    def get_left_boundary(self):
        left, right = self.getBoundaries()
        return left
    
    def get_right_boundary(self):
        left, right = self.getBoundaries()
        return right
    
    def get_child_left_boundary(self, childNumber):
        if childNumber < len(self.children):
            return self.children[childNumber].get_left_boundary()
        return self.children[-1].get_right_boundary()

    def get_child_right_boundary(self, childNumber):
        childNumber -= 1
        if childNumber >= 0:
            return self.children[childNumber].get_right_boundary()
        return self.children[0].get_left_boundary()

    def get_child_boundaries(self, childNumber):
        assert childNumber >= 0 and childNumber < len(self.children)
        return self.children[childNumber].getBoundaries()

    def get_encloser(self):
        return self.enclosingFaceRoot if self.isFace else self.parent.enclosingFaceRoot

    def getBoundaries(self):
        # if is layer 0 leaf return x, y
        if self.u.layer == 0:
            return [self.u], [self.v]

        f = self.get_encloser()
        q = self.lb - 1
        t = self.rb - 1

        return f.get_child_left_boundary(q) + [self.u], f.get_child_right_boundary(t) + [self.v]

    def solve(self, graph):
        
        # 1) - v is a face vertex that doesn't enclose any component
        if self.isFace and len(self.enclosedComponents) == 0:
            T = self.children[0].solve(graph)
            for i in range(1, len(self.children)):
                T = T.merge(self.children[i].solve(graph))

            T = T.adjust()
            return T
        
        # 2) - v is a face vertex that encloses a component
        if self.isFace and len(self.enclosedComponents) > 0:
            T = self.enclosedComponents[0].rootedTree.solve(graph)
            T = T.contract()
            T = T.adjust()
            return T
        
        # 3) - v is a level 0 leaf
        if self.u.layer == 0 and self.is_leaf():
            T = Table(graph, [self.u], [self.v])
            T = T.create_edge_table(self)
            return T
        
        # 4) - v is a layer > 0 leaf
        x = self.u
        y = self.v
        f = self.get_encloser()
        p = None
        # At some point there was self.rb + 1, but it exceeded the array bounds
        # but I don't know why if it shouldn't be checked as special case
        for i in range(self.lb, self.rb):
            zi = f.children[i - 1].u
            if graph.has_edge(y.id, zi.id):
                p = i
                break
        if p is None:
            p = self.rb

        T = Table(graph, [x], [y])
        T = T.create(self, p)
        j = p - 1
        while j >= self.lb:
            temp = f.children[j - 1].solve(graph)
            temp = temp.extend(x)
            T = temp.merge(T)
            j -= 1
        j = p
        while j < self.rb:
            temp = f.children[j - 1].solve(graph)
            temp = temp.extend(y)
            T = T.merge(temp)
            j += 1
        return T

class RootedTree:
    def __init__(self):
        self.root = None
        self.faces = []
        self.facesProcessed = 0

    def process_spanning_tree(self, spanningTree: SpanningTree):
        assert spanningTree.root_face is not None and spanningTree.root_face.isFace
        e0 = spanningTree.root_face.data.edges[0]
        e1 = spanningTree.root_face.data.edges[1]
        commonVertex = e0.get_common_vertex(e1)
        rootVertex = e0.get_other_vertex(commonVertex)
        self.root = RootedNode(spanningTree.root_face.data, rootVertex, rootVertex, True)

        self.process_node(self.root, spanningTree.root_face)

    def process_node(self, root: RootedNode, node: SpanningNode, excepting: SpanningNode = None):        
        # is inner edge
        if node.is_connecting_edge():
            nextFace = node.get_other_face(root.data)
            newRoot = RootedNode(nextFace.data, node.data.u, node.data.v, True)
            root.add_child(newRoot)
            self.process_node(newRoot, nextFace, node)

            return
        
        # is outer edge
        if not node.isFace:
            if root.last_child_vertex().id == node.data.u.id:
                root.add_child(RootedNode(node.data, node.data.u, node.data.v))
            else:
                root.add_child(RootedNode(node.data, node.data.v, node.data.u))
            return
        
        # is face
        self.facesProcessed += 1
        self.faces.append(node.data)
        for neighbor in node.neighbors:
            if neighbor == excepting:
                continue
            self.process_node(root, neighbor)

    def order_children(self, root: RootedNode):
        if len(root.children) == 0:
            return

        u = root.u
        for i in range(len(root.children)):
            if root.children[i].vertex_in(u):
                root.children = root.children[i:] + root.children[:i]
                break
        

        # i don't know if it covers all cases or if it doesn't break something else
        if root.children[0].u.id != u.id:
            root.children[0].swap_uv()
        if root.children[0].v.id != root.children[1].u.id and root.children[0].v.id != root.children[1].v.id:
            root.children = root.children[:1] + list(reversed(root.children[1:]))

        for child in root.children:
            if child.u.id != u.id:
                child.swap_uv()
            u = child.v

        for child in root.children:
            self.order_children(child)

    def process_cutpoints(self, spanningTree: SpanningTree):
        # check all faces
        for faceNode in spanningTree.faces:
            face = faceNode.data
            if face not in self.faces:
                for usedFace in self.faces:
                    intersectionVertex = face.intersection_vertex(usedFace)
                    if intersectionVertex is not None:
                        break
                if intersectionVertex is None:
                    continue # face is not directly connected via cutpoint to processed graph

                faceRoot = RootedNode(face, intersectionVertex, intersectionVertex, True)
                self.process_node(faceRoot, faceNode)
                self.root.add_subtree(faceRoot)
    def reverse(self):
        assert self.root is not None
        self.root.reverse()

    def calculate_lbrb(self, graph):
        leaves = self.root.get_leaves()
        encloserChildren = self.root.enclosingFaceRoot.children

        r = len(encloserChildren)

        # Init LB(v1) and RB(vn)
        leaves[0].lb = 1
        leaves[-1].rb = r + 1

        # Calculate LB(vj) for j = 2, ..., n
        for j in range(1, len(leaves)):
            vj = leaves[j]
            i = leaves[j-1].lb
            while True:
                hasEdge = graph.has_edge(vj.u.id, encloserChildren[i - 1].u.id)
                if hasEdge:
                    q = i # why is there +1? -> there was once
                    vj.lb = q 
                    leaves[j -1].rb = q
                    break
                i += 1

        self.root.finalize_lbrb()

    def solve(self, graph):
        return self.root.solve(graph)
