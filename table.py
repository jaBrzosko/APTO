# x and y are list of separators
# First element is on smallest layer, then it's rising
# Keys in value determine whether each element is present
# We use ints and treat them as bits
class Table:
    def __init__(self, graph, x, y):
        self.value = {}
        self.x = x
        self.y = y
        self.graph = graph

        

    def get(self, i, j):
        return self.value[(i, j)]

    def set(self, i, j, value):
        self.value[(i, j)] = value
    
    def create_edge_table(self, v):
        self.x = [v.u]
        self.y = [v.v]
        self.value[(0, 0)] = 0
        self.value[(1, 0)] = v.u.weight
        self.value[(0, 1)] = v.v.weight
        self.value[(1, 1)] = None
        return self
    
    def adjust(self):
        u = self.x[-1]
        v = self.y[-1]
        if u.id == v.id:
            # null entries where only one of (u, v) is present
            # when both are present substract one
            for k in self.value:
                uPresent = last_bit(k[0])
                vPresent = last_bit(k[1])
                if uPresent != vPresent:
                    self.set(k[0], k[1], None)
                elif uPresent == 1 and vPresent == 1:
                    value = self.get(k[0], k[1])
                    self.set(k[0], k[1], None if value is None else value - 1)

        elif self.graph.has_real_edge(u.id, v.id):
            # null entries where both are present
            for k in self.value:
                uPresent = last_bit(k[0])
                vPresent = last_bit(k[1])
                if uPresent == 1 and vPresent == 1:
                    self.set(k[0], k[1], None)
        return self

    def merge(self, T):
        assert len(self.y) == len(T.x)
        for i in range(len(self.y)):
            assert self.y[i].id == T.x[i].id
        O = Table(self.graph, self.x, T.y)
        maxSep = sepSizeN(len(self.x))
        for ls in range(maxSep + 1):
            for rs in range(maxSep + 1):
                p = None
                for ms in range(maxSep + 1):
                    t1V = self.get(ls, ms)
                    t2V = T.get(ms, rs)
                    if t1V is None or t2V is None:
                        continue
                    v = t1V + t2V - count_bits(ms)
                    if p is None or v > p:
                        p = v
                O.set(ls, rs, p)
        return O

    def contract(self):
        # assert self.x[-1].id == self.y[-1].id
        O = Table(self.graph, self.x[:-1], self.y[:-1])
        newSep = sepSizeN(len(self.x) - 1)
        for ls in range(newSep + 1):
            for rs in range(newSep + 1):
                isIn = self.get(ls * 2 + 1, rs * 2 + 1)
                isOut = self.get(ls * 2, rs * 2)
                if isIn is None:
                    if isOut is None:
                        O.set(ls, rs, None)
                    else:
                        O.set(ls, rs, isOut)
                elif isOut is None or isOut < isIn:
                    O.set(ls, rs, isIn)
                else:
                    O.set(ls, rs, isOut)
        return O

    def create(self, v, p):
        # WARNING: May need to change p to p-1 or something like that
        f = v.get_encloser()
        
        p -= 1 # <- TEST

        # we have common boundary for left and right
        # table will represent this boundary and edge (v.u, v.v)
        boundary = f.get_child_left_boundary(p) if p <= len(f.children) else f.get_child_right_boundary(p - 1)
        maxSep = sepSizeN(len(boundary) + 1)
        for ls in range(maxSep + 1):
            for rs in range(maxSep + 1):
                commonLeft = ls >> 1
                commonRight = rs >> 1
                uBit = last_bit(ls)
                vBit = last_bit(rs)
                # if separator is not equivalent or last bits are both present then we None it and continue
                if commonLeft != commonRight or (uBit == vBit == 1):
                    self.set(ls, rs, None)
                    continue

                # ls and rs are the same except for last bit
                
                # check whether edge in common separator doesn't have both vertices included
                skip = False
                common = bits(commonLeft)
                for i in range(len(common) - 1):
                    if common[i] == common[i + 1] and self.graph.has_real_edge(boundary[i].id, boundary[i + 1].id):
                        self.set(ls, rs, None)
                        skip = True
                        break
                if skip:
                    continue

                # skip when (u, v) edge is connected to last vertex in common separator
                lastVertex = boundary[-1]
                if common[-1] == uBit == 1 and self.graph.has_real_edge(lastVertex.id, v.u.id):
                    self.set(ls, rs, None)
                    continue
                if common[-1] == vBit == 1 and self.graph.has_real_edge(lastVertex.id, v.v.id):
                    self.set(ls, rs, None)
                    continue
                
                # last set
                self.set(ls, rs, max(count_bits(ls), count_bits(rs)))

        self.x = boundary + [v.u]
        self.y = boundary + [v.v]
        return self

    def extend(self, z):
        O = Table(self.graph, self.x + [z], self.y + [z])
        newSep = sepSizeN(len(self.x) + 1)
        for ls in range(newSep + 1):
            for rs in range(newSep + 1):
                zInLs = last_bit(ls)
                zInRs = last_bit(rs)
                if zInLs != zInRs:
                    O.set(ls, rs, None)
                    continue
                if zInLs == zInRs == 0:
                    O.set(ls, rs, self.get(ls >> 1, rs >> 1))
                    continue
                if self.graph.has_real_edge(self.x[-1].id, z.id) or self.graph.has_real_edge(self.y[-1].id, z.id):
                    O.set(ls, rs, None)
                else:
                    v = self.get(ls >> 1, rs >> 1)
                    if v is None:
                        O.set(ls, rs, None)
                    else:
                        O.set(ls, rs, v + 1)
        return O

    def print(self):
        print("Table:")
        maxSep = sepSizeN(len(self.x))
        print("***")
        for ls in range(maxSep + 1):
            for rs in range(maxSep + 1):
                left = bin(ls)[2:]
                right = bin(rs)[2:]
                print(left, right, self.get(ls, rs))
            print("***")

def last_bit(n):
    return n & 1

def bits(n):
    return [int(x) for x in bin(n)[2:]]

def count_bits(n):
    return bin(n).count("1")

def sepSizeN(n):
    return 2**n - 1

