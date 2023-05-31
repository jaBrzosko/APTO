from table import Table
from rooted import RootedTree
from spanning import SpanningTree
from vertex import Vertex
from edge import Edge, Embeding, Face

class Collection:
    def __init__(self):
        self.edges = {}
        self.vertices = {}
        self.faces = []
        self.spanningTree = SpanningTree()
        self.rootedTree = RootedTree()
        self.numberOfLayers = 0
        self.layers = []
    
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
    
    def create_vertex(self, vertexId, layer):
        if vertexId in self.vertices:
            return self.get_vertex(vertexId)
        vertex = Vertex(vertexId, layer)
        return vertex

    def load_file(self, path):
        with open(path) as f:
            f = f.read().split('\n')[:-1]
        for line in f:
            data = line.split(';')
            edgeId = int(data[0])
            uId = int(data[1])
            vId = int(data[2])
            layer1 = int(float(data[7]))
            layer2 = int(float(data[8]))

            if layer1 > self.numberOfLayers:
                self.numberOfLayers = layer1
            if layer2 > self.numberOfLayers:
                self.numberOfLayers = layer2

            u = self.create_vertex(uId, layer1)
            v = self.create_vertex(vId, layer2)
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
    
    def create_layers(self):
        pass

    def materialize(self):
        for vertex in self.vertices.values():
            vertex.init_clockwise_vertices()
            vertex.init_counterclockwise_vertices()
            vertex.reverse_layer(self.numberOfLayers)

    def create_faces(self):

        clockwise_edges = []
        counter_clockwise_edges = []

        for vertex in self.vertices.values():
            vertexNode = vertex.clockwise_vertices.head
            firstRun = True
            while vertexNode != vertex.clockwise_vertices.head or firstRun:
                firstRun = False
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
                face = Face(len(self.faces))
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
        

        # remove face with all vertices
        for face in self.faces:
            visited_vertices = []
            for edge in face.edges:
                if edge.u.id not in visited_vertices:
                    visited_vertices.append(edge.u.id)
                if edge.v.id not in visited_vertices:
                    visited_vertices.append(edge.v.id)
            if len(visited_vertices) == len(self.vertices):
                self.faces.remove(face)
                break

        # fix bridges
        edgesInFaces = []
        for face in self.faces:
            for edge in face.edges:
                edgesInFaces.append(edge)

        for edge in self.edges.values():
            if edge in edgesInFaces:
                continue
            face = Face(len(self.faces) + 1)
            reversedEdge = Edge(-edge.id, edge.v, edge.u)
            reversedEmbeding = Embeding(edge.embeding.c1, edge, edge, edge.embeding.cc2)
            newEmbeding = Embeding(reversedEdge, edge.embeding.c2, edge.embeding.cc1, reversedEdge)
            reversedEdge.set_embeding(reversedEmbeding)
            edge.set_embeding(newEmbeding)
            face.add_edge(edge)
            face.add_edge(reversedEdge)
            self.faces.append(face)
        
    def create_spanning_tree(self):
        for face in self.faces:
            self.spanningTree.process_face(face)
        self.rootedTree.process_spanning_tree(self.spanningTree)
        self.rootedTree.order_children(self.rootedTree.root)
        # check if all faces are covered in rooted tree
        while self.rootedTree.facesProcessed != len(self.faces):
            self.rootedTree.process_cutpoints(self.spanningTree)

    def solve(self):
        return self.table(self.rootedTree.root)
    
    def table(self, v):
        if v.is_leaf():
            tab = Table(v.u, v.v)
            tab.create_edge_table()
            return tab
        T = self.table(v.first_child())

        for i in range(1, len(v.children)):
            Ti = self.table(v.children[i])
            T = T.merge(Ti)
        T.adjust()
        return T
