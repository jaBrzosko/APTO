from vertex import Vertex


class Table:
    def __init__(self, u: Vertex, v: Vertex):
        self.value = {}
        self.u = u
        self.v = v

    def create_edge_table(self):
        self.value[(0, 0)] = 0
        self.value[(0, 1)] = 1
        self.value[(1, 0)] = 1
        self.value[(1, 1)] = None

    def adjust(self):
        if self.u == self.v:
            for k in self.value:
                if k[0] != k[1]:
                    self.value[k] = None
                if k[0] == k[1] == 1:
                    self.value[k] = self.value[k] - 1
        else:
            for k in self.value:
                if k[0] == k[1] == 1:
                    self.value[k] = None
    
    def get(self, i, j):
        return self.value[(i, j)]

    def set(self, i, j, value):
        self.value[(i, j)] = value

    def merge(self, T):
        assert self.v == T.u
        out = Table(self.u, T.v)
        for x in range(2):
            for y in range(2):
                best = None
                for b in range(2):
                    try:
                        v = self.get(x, b) + T.get(b, y) - b.bit_count()
                    except TypeError:
                        continue
                    if best is None or v > best:
                        best = v
                out.set(x, y, best)
        return out

