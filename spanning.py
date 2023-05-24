from edge import Face


class SpanningNode:
    def __init__(self, data, isFace = False):
        self.data = data
        self.isFace = isFace
        self.neighbors = []

    def is_connecting_edge(self):
        return not self.isFace and len(self.neighbors) == 2
    
    def get_other_face(self, face):
        assert self.is_connecting_edge()
        return self.neighbors[0] if self.neighbors[0].data.id != face.id else self.neighbors[1]

class SpanningTree:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.root_face = None

    def add_node(self, node):
        if node not in self.vertices:
            self.vertices.append(node)

    def create_edge_node(self, edge):
        for v in self.vertices:
            if not v.isFace and v.data.id == edge.id:
                return v
        return SpanningNode(edge)

    def process_face(self, face: Face):
        faceNode = SpanningNode(face, True)
        if self.root_face is None:
            self.root_face = faceNode
        self.add_node(faceNode)
        self.faces.append(faceNode)
        for edge in face.edges:
            edgeNode = self.create_edge_node(edge)
            self.add_node(edgeNode)
            faceNode.neighbors.append(edgeNode)
            edgeNode.neighbors.append(faceNode)

