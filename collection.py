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
            vertex.set_collection(self)

    def get_edge(self, edgeId):
        return self.edges[edgeId]
    
    def get_vertex(self, vertexId):
        return self.vertices[vertexId]
    
    def has_real_edge(self, uId, vId):
        assert uId in self.vertices and vId in self.vertices
        u = self.get_vertex(uId)
        v = self.get_vertex(vId)
        edge = u.get_edge_to(v)
        return edge is not None and not edge.isFake

    def has_edge(self, uId, vId):
        assert uId in self.vertices and vId in self.vertices
        u = self.get_vertex(uId)
        v = self.get_vertex(vId)
        edge = u.get_edge_to(v)
        return edge is not None

    def create_vertex(self, vertexId, layer, weight=1):
        if vertexId in self.vertices:
            return self.get_vertex(vertexId)
        vertex = Vertex(vertexId, layer, weight=weight)
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

    def reverse_layers(self):
        for vertex in self.vertices.values():
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
        # I', not sure if those faces won't have to be counterclockwise
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
    
    def traingulate(self):
        copiedEdges = self.edges.copy()
        for edge in copiedEdges.values():
            if not edge.is_layer_connecting():
                continue
            # I am not sure why it works, I thought it needed more logic
            while True:
                smallerVertex = edge.get_smaller_layer_vertex()
                clockwiseEdge = edge.get_clockwise_edge(smallerVertex)
                sameLayerVertex = clockwiseEdge.get_other_vertex(smallerVertex)
                otherVertex = edge.get_other_vertex(smallerVertex)
                if sameLayerVertex.layer != smallerVertex.layer:
                    break

                maybeEdge = otherVertex.get_edge_to(sameLayerVertex)
                if maybeEdge is not None:
                    break
                # print("New edge between " + str(otherVertex.id) + " and " + str(sameLayerVertex.id))
                edge = self.add_fake_edge(edge, clockwiseEdge)

    # e2 has to be clockwise to e1
    def add_fake_edge(self, e1, e2):
        commonVertex = e1.get_common_vertex(e2)
        assert commonVertex is not None and e1.get_clockwise_edge(commonVertex) == e2
        u = e1.get_other_vertex(commonVertex)
        v = e2.get_other_vertex(commonVertex)
        fakeEdge = Edge(-len(self.edges), u, v, True)
        e1_cc = e1.get_counterclockwise_edge(u)
        e2_c = e2.get_clockwise_edge(v)
        fakeEmbedding = Embeding(e1, e2_c, e1_cc, e2)
        fakeEdge.set_embeding(fakeEmbedding)
        self.add_edge(fakeEdge)
        e1.set_counterclockwise_edge(u, fakeEdge)
        e2.set_clockwise_edge(v, fakeEdge)
        e1_cc.set_clockwise_edge(u, fakeEdge)
        e2_c.set_counterclockwise_edge(v, fakeEdge)

        return fakeEdge

    def set_fake_vertex_copy(self, vertexId, fakeVertex):
        v = self.get_vertex(vertexId)
        v.fakeCopy = fakeVertex

    def load_as_layer(self, collection, layerNumber):
        for edge in collection.edges.values():
            if edge.u.layer == edge.v.layer == layerNumber:
                u = self.create_vertex(edge.u.id, layerNumber, edge.u.weight)
                v = self.create_vertex(edge.v.id, layerNumber, edge.v.weight)
                collection.set_fake_vertex_copy(edge.u.id, u)
                collection.set_fake_vertex_copy(edge.v.id, v)        
                self.add_edge(Edge(edge.id, u, v))
        for edgeId in self.edges:
            edge = self.edges[edgeId]
            originalEmeding = collection.edges[edgeId].embeding
            
            # clockwise to u (c1)
            ec1 = originalEmeding.c1
            c1Vertex = ec1.get_other_vertex(edge.u)
            while c1Vertex.layer != layerNumber:
                ec1 = ec1.get_clockwise_edge(edge.u)
                c1Vertex = ec1.get_other_vertex(edge.u)

            # clockwise to v (c2)
            ec2 = originalEmeding.c2
            c2Vertex = ec2.get_other_vertex(edge.v)
            while c2Vertex.layer != layerNumber:
                ec2 = ec2.get_clockwise_edge(edge.v)
                c2Vertex = ec2.get_other_vertex(edge.v)

            # counterclockwise to u (cc1)
            ecc1 = originalEmeding.cc1
            cc1Vertex = ecc1.get_other_vertex(edge.u)
            while cc1Vertex.layer != layerNumber:
                ecc1 = ecc1.get_counterclockwise_edge(edge.u)
                cc1Vertex = ecc1.get_other_vertex(edge.u)

            # counterclockwise to v (cc2)
            ecc2 = originalEmeding.cc2
            cc2Vertex = ecc2.get_other_vertex(edge.v)
            while cc2Vertex.layer != layerNumber:
                ecc2 = ecc2.get_counterclockwise_edge(edge.v)
                cc2Vertex = ecc2.get_other_vertex(edge.v)

            ec1 = self.get_edge(ec1.id)
            ec2 = self.get_edge(ec2.id)
            ecc1 = self.get_edge(ecc1.id)
            ecc2 = self.get_edge(ecc2.id)


            edge.set_embeding(Embeding(ec1, ec2, ecc1, ecc2))

    def make_layers(self):

        for i in range(self.numberOfLayers + 1):
            layer = Collection()
            layer.load_as_layer(self, i)
            self.layers.append(layer)

    def split(self):
        k0 = next(iter(self.vertices))
        visitedVertices = [self.vertices[k0]]
        visitedEdges = []
        index = 0

        while index < len(visitedVertices):
            vertex = visitedVertices[index]
            for edge in vertex.edges:
                if edge not in visitedEdges:
                    visitedEdges.append(edge)
                other = edge.get_other_vertex(vertex)
                if other not in visitedVertices:
                    visitedVertices.append(other)
            index += 1
        if len(visitedVertices) == len(self.vertices):
            return None
        newLayer = Collection()

        for edge in visitedEdges:
            self.edges.pop(edge.id)
            newLayer.edges[edge.id] = edge

        for vertex in visitedVertices:
            self.vertices.pop(vertex.id)
            newLayer.vertices[vertex.id] = vertex
            vertex.set_collection(newLayer)

        return newLayer

    def split_layers(self):
        layersToBeAdded = []
        for layer in self.layers:
            while True:
                newLayer = layer.split()
                if newLayer is None:
                    break
                layersToBeAdded.append(newLayer)
        for layer in layersToBeAdded:
            self.layers.append(layer)

    def materialize_faces(self):
        for layer in self.layers:
            layer.materialize()

    def create_layers_faces(self):
        for layer in self.layers:
            layer.create_faces()

    def create_layers_spanning_trees(self):
        for layer in self.layers:
            layer.create_spanning_tree()

    def check_reversing(self):
        for layer in self.layers:                
            # check if layer is polygon and needs to be reversed
            k0 = next(iter(layer.vertices))
            if layer.vertices[k0].layer == self.numberOfLayers:
                self.check_if_reverse_is_needed(layer, True)
            else:
                self.check_if_reverse_is_needed(layer, False)

        

    def check_if_reverse_is_needed(self, layer, checkClockwise):
        face0 = layer.faces[0]
        e0Id = face0.edges[0].id
        e1Id = face0.edges[1].id

        e0 = self.get_edge(e0Id)
        e1 = self.get_edge(e1Id)
        
        commonVertex = e0.get_common_vertex(e1)
        if checkClockwise:
            edge = e1.get_clockwise_edge(commonVertex)
        else:
            edge = e1.get_counterclockwise_edge(commonVertex)
        # we want this edge to be between {i}-th and {i+1}-th layer
        if edge.get_other_vertex(commonVertex).layer != commonVertex.layer + (-1 if checkClockwise else 1):
            layer.faces[0].edges.reverse()

    def find_encloseres(self):
        for layer in self.layers:
            k0 = next(iter(layer.vertices))
            if layer.vertices[k0].layer == self.numberOfLayers:
                # skip most inner layer
                continue
            for face in layer.faces:
                enclosedLayers = []
                index = 0
                L = len(face.edges)
                while index < L:
                    e0Id = face.edges[index].id
                    e1Id = face.edges[(index + 1) % L].id
                    e0 = self.get_edge(e0Id)
                    e1 = self.get_edge(e1Id)
                    commonVertex = e0.get_common_vertex(e1)
                    ccEdge = e1.get_counterclockwise_edge(commonVertex)
                    while ccEdge != e0:
                        otherVertexId = ccEdge.get_other_vertex(commonVertex).id
                        inLayer = self.get_vertex(otherVertexId).fakeCopy.fatherCollection
                        if inLayer not in enclosedLayers:
                            enclosedLayers.append(inLayer)
                        ccEdge = ccEdge.get_counterclockwise_edge(commonVertex)
                    index += 1
                faceRoot = layer.rootedTree.root.find_face_root(face)
                for enclosedLayer in enclosedLayers:
                    faceRoot.add_enclosed_component(enclosedLayer)
                # print("Face: ", [e.id for e in face.edges])
                # for enclosedLayer in enclosedLayers:
                    # print("Enclosed layer: ", [e.id for e in enclosedLayer.edges.values()])

    def calculate_lbrb(self):
        for layer in self.layers:
            k0 = next(iter(layer.vertices))
            if layer.vertices[k0].layer == 0:
                # skip most outer layer
                continue
            layer.rootedTree.calculate_lbrb(self)

    def solve(self):
        for layer in self.layers:
            k0 = next(iter(layer.vertices))
            if layer.vertices[k0].layer != 0:
                # skip inner layers
                continue
            return layer.rootedTree.solve(self)

