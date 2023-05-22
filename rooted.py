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

    def add_child(self, child):
        self.children.append(child)
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

class RootedTree:
    def __init__(self):
        self.root = None

    def process_spanning_tree(self, spanningTree: SpanningTree):
        assert spanningTree.root_face is not None and spanningTree.root_face.isFace
        rootVertex = spanningTree.root_face.data.edges[0].u
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
        for child in root.children:
            if child.u.id != u.id:
                child.swap_uv()
            u = child.v

        for child in root.children:
            self.order_children(child)



    def add_face(self, face):
        pass

    def add_edge(self, edge):
        pass
