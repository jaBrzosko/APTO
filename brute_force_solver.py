class Vertex:
    def __init__(self, id: int = -1, weight: int = 1) -> None:
        self.id: int = id
        self.weight: int = weight
        self.marked: bool = False
        self.neighbours: list[Vertex] = []

class Graph:
    def __init__(self) -> None:
        self.vertices = []

    def add_vertex(self, id: int = -1, weight: int = 1) -> Vertex:
        new = Vertex(id, weight)
        self.vertices.append(new)
        return new

    def add_edge(self, id1: int, id2: int) -> None:
        v1 = next((v for v in self.vertices if v.id == id1), None)
        if(v1 == None):
            v1 = self.add_vertex(id1)
        
        v2 = next((v for v in self.vertices if v.id == id2), None)
        if(v2 == None):
            v2 = self.add_vertex(id2)

        v1.neighbours.append(v2)
        v2.neighbours.append(v1)

    def parse_file(self, path: str) -> None:
        self.vertices = []
        with open(path) as f:
            f = f.read().split('\n')[:-1]
        for line in f:
            data = line.split(';')
            id1 = int(data[1])
            id2 = int(data[2])

            self.add_edge(id1, id2)
    
    def print_graph(self) -> None:
        for v in self.vertices:
            print(str(v.id) + ": " + str([v.id for v in v.neighbours]))

def brute_force(g: Graph, val: int) -> int:
    verts: list[Vertex] = [v for v in g.vertices if v.marked == False]
    temp = val
    #print([v.id for v in verts])
    if(len(verts) == 0):
        return val
    for v in verts:
        unmarked = [v for v in v.neighbours if v.marked == False]
        for v_to_mark in unmarked:
            v_to_mark.marked = True
        v.marked = True
        temp = max(val, brute_force(g, val + v.weight))
        for v_to_mark in unmarked:
            v_to_mark.marked = False
        v.marked = False
    return temp
    

def main():
    g = Graph()
    #g.parse_file("/home/user/repos/APTO/graphs/HexaGraph.txt")
    g.parse_file("./graphs/twoSecondLayers.txt")
    # g.print_graph()
    print(brute_force(g, 0))

if __name__ == '__main__':
    main()
