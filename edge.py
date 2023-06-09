class Edge:
    def __init__(self, id, u, v, isFake = False):
        self.id = id
        self.u = u
        self.v = v
        self.embeding = None
        self.isFake = isFake

    def set_embeding(self, embeding):
        self.embeding = embeding
    
    def get_other_vertex(self, u):
        return self.v if u.id == self.u.id else self.u
    
    def get_clockwise_edge(self, u):
        return self.embeding.c1 if u.id == self.u.id else self.embeding.c2
    
    def get_counterclockwise_edge(self, u):
        return self.embeding.cc1 if u.id == self.u.id else self.embeding.cc2
    
    def get_smaller_layer_vertex(self):
        return self.u if self.u.layer < self.v.layer else self.v

    def get_common_vertex(self, edge):
        assert self.u.id == edge.u.id or self.u.id == edge.v.id or self.v.id == edge.u.id or self.v.id == edge.v.id
        return self.u if self.u.id == edge.u.id or self.u.id == edge.v.id else self.v

    def set_clockwise_edge(self, u, edge):
        assert self.u.id == u.id or self.v.id == u.id
        if u.id == self.u.id:
            self.embeding.c1 = edge
        else:
            self.embeding.c2 = edge
    
    def set_counterclockwise_edge(self, u, edge):
        assert self.u.id == u.id or self.v.id == u.id
        if u.id == self.u.id:
            self.embeding.cc1 = edge
        else:
            self.embeding.cc2 = edge

    def is_clockwise(self, u, v):
        assert self.u.id == u.id or self.v.id == u.id
        assert self.u.id == v.id or self.v.id == v.id

        return self.u.id == u.id and self.v.id == v.id
    
    def is_vertex_in(self, u):
        return self.u.id == u.id or self.v.id == u.id
    
    def is_layer_connecting(self):
        return self.u.layer != self.v.layer
    
class Embeding:
    def __init__(self, c1, c2, cc1, cc2):
        self.c1 = c1
        self.c2 = c2
        self.cc1 = cc1
        self.cc2 = cc2

class Face:
    def __init__(self, id):
        self.id = id
        self.edges = []

    def add_edge(self, edge):
        self.edges.append(edge)

    def intersection_vertex(self, face):
        for edge in self.edges:
            for other_edge in face.edges:
                if edge.u.id == other_edge.u.id or edge.u.id == other_edge.v.id:
                    return edge.u
                if edge.v.id == other_edge.u.id or edge.v.id == other_edge.v.id:
                    return edge.v
        return None
