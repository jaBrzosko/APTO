from cyclic import CLL


class Vertex:
    def __init__(self, id, layer, weight=1):
        self.id = id
        self.weight = weight
        self.edges = []
        self.layer = layer
        self.clockwise_vertices = CLL()
        self.counterclockwise_vertices = CLL()

    def reverse_layer(self, maxLayer):
        self.layer = maxLayer - self.layer

    def set_layer(self, layer):
        self.layer = layer

    def add_edge(self, edge):
        self.edges.append(edge)
    
    def init_clockwise_vertices(self):
        self.clockwise_vertices = CLL()
        counter = 0
        edge = self.edges[0]

        while counter != len(self.edges):
            self.clockwise_vertices.add_to_end(edge.get_other_vertex(self))
            edge = edge.get_clockwise_edge(self)
            counter += 1

    def init_counterclockwise_vertices(self):
        self.counterclockwise_vertices = CLL()
        counter = 0
        edge = self.edges[0]

        while counter != len(self.edges):
            self.counterclockwise_vertices.add_to_end(edge.get_other_vertex(self))
            edge = edge.get_counterclockwise_edge(self)
            counter += 1

    def get_next_after(self, vertex):
        node = self.clockwise_vertices.head
        while node.data.id != vertex.id:
            node = node.next
        return node.next.data
    
    def get_edge_to(self, vertex):
        for edge in self.edges:
            if edge.get_other_vertex(self).id == vertex.id:
                return edge
            
