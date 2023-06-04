from spanning import SpanningNode, SpanningTree
from vertex import Vertex


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
        self.enclosingFace = None
        self.enclosedRoots = []

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
