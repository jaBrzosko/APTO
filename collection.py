from vertex import Vertex
from edge import Edge, Embeding, Face

class Collection:
    def __init__(self):
        self.edges = {}
        self.vertices = {}
        self.faces = []
    
    def add_edge(self, edge):
        self.edges[edge.id] = edge
        
        self.add_vertex(edge.u)
        self.add_vertex(edge.v)
        
        self.vertices[edge.u.id].add_edge(edge)
        self.vertices[edge.v.id].add_edge(edge)

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def get_edge(self, edgeId):
        return self.edges[edgeId]
    
    def get_vertex(self, vertexId):
        return self.vertices[vertexId]
    
    def create_vertex(self, vertexId):
        if vertexId in self.vertices:
            return self.get_vertex(vertexId)
        vertex = Vertex(vertexId)
        return vertex

    def load_file(self, path):
        with open(path) as f:
            f = f.read().split('\n')[:-1]
        for line in f:
            data = line.split(';')
            edgeId = int(data[0])
            uId = int(data[1])
            vId = int(data[2])
            u = self.create_vertex(uId)
            v = self.create_vertex(vId)
            edge = Edge(edgeId, u, v)
            self.add_edge(edge)
        for line in f:
            data = line.split(';')
            c1 = self.get_edge(int(data[3]))
            c2 = self.get_edge(int(data[4]))
            cc1 = self.get_edge(int(data[5]))
            cc2 = self.get_edge(int(data[6]))

            embeding = Embeding(c1, c2, cc1, cc2)
            self.get_edge(int(data[0])).set_embeding(embeding)
    
    def materialize(self):
        for vertex in self.vertices.values():
            vertex.init_clockwise_vertices()

    def create_faces(self):

        clockwise_edges = []
        counter_clockwise_edges = []

        for vertex in self.vertices.values():
            vertexNode = vertex.clockwise_vertices.head
            while vertexNode.next != vertex.clockwise_vertices.head:
                # get edge object and check if we already were there
                edge = vertex.get_edge_to(vertexNode.data)
                if edge.is_clockwise(vertex, vertexNode.data):
                    if edge in clockwise_edges:
                        vertexNode = vertexNode.next
                        continue
                    clockwise_edges.append(edge)
                else:
                    if edge in counter_clockwise_edges:
                        vertexNode = vertexNode.next
                        continue
                    counter_clockwise_edges.append(edge)
                
                # create face
                face = Face()
                face.add_edge(edge)
                u = vertex
                v = vertexNode.data
                while v.id != vertex.id:
                    w = v.get_next_after(u)
                    u = v
                    v = w
                    edge = u.get_edge_to(v)
                    if edge.is_clockwise(u, v):
                        clockwise_edges.append(edge)
                    else:
                        counter_clockwise_edges.append(edge)
                    face.add_edge(edge)
                
                # save face
                self.faces.append(face)
