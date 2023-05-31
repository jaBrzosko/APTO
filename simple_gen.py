from enum import Enum
from random import random
class Dirs(Enum):
    up = 0
    right = 1
    down = 2
    left = 3

class Node:
    def __init__(self) -> None:
        self.dirs = [False, False, False, False]

class Crate:
    def __init__(self, w, h) -> None:
        self.w = w
        self.h = h
        self.mat = [[Node() for _ in range(w)] for _ in range(h)] 
    
    def generate(self) -> None:
        for i in range(self.h):
            for j in range(self.w):
                if i >= j and i < self.h - j - 1 or i < j - self.w + self.h and i >= self.w - j - 1:
                    self.mat[i][j].dirs[Dirs.down.value] = True
                if i > j and i <= self.h - j - 1 or i <= j - self.w + self.h and i > self.w - j - 1:
                    self.mat[i][j].dirs[Dirs.up.value] = True
                if j >= i and j < self.w - i - 1 or j < i - self.h + self.w and j >= self.h - i - 1:
                    self.mat[i][j].dirs[Dirs.right.value] = True
                if j > i and j <= self.w - i - 1 or j <= i - self.h + self.w and j > self.h - i - 1:
                    self.mat[i][j].dirs[Dirs.left.value] = True

    def print(self) -> None:
        for i in range(self.h):
            print()
            for j in range(self.w):
                print(f"({i},{j})", end="")
                if j + 1 < self.w and self.mat[i][j].dirs[Dirs.right.value] and self.mat[i][j + 1].dirs[Dirs.left.value]:
                    print("---", end="")
                elif j + 1 == self.w or not self.mat[i][j].dirs[Dirs.right.value] and not self.mat[i][j + 1].dirs[Dirs.left.value]:
                    print("   ", end="")
                else:
                    print("XXX", end="")
            for _ in range(2):
                print()
                for j in range(self.w):
                    if i + 1 < self.h and self.mat[i][j].dirs[Dirs.down.value] and self.mat[i + 1][j].dirs[Dirs.up.value]:
                        print("  | ", end="")
                    elif i + 1 == self.h or not self.mat[i][j].dirs[Dirs.down.value] and not self.mat[i + 1][j].dirs[Dirs.up.value]:
                        print("    ", end="")
                    else:
                        print("  X ", end="")
                    print("    ", end="")
        print()

    def dir_to_val(self, dir):
        if dir.value == Dirs.down.value:
            return self.w
        if dir.value == Dirs.up.value:
            return -self.w
        if dir.value == Dirs.left.value:
            return -1
        if dir.value == Dirs.right.value:
            return 1
        
    def randomize(self, prob = 0.5) -> None:
        for i in range(self.h):
            for j in range(self.w):
                if prob > random() and i != self.h - 1:
                    self.mat[i + 1][j].dirs[Dirs.up.value] = True
                    self.mat[i][j].dirs[Dirs.down.value] = True
                if prob > random() and j != self.w - 1:
                    self.mat[i][j + 1].dirs[Dirs.left.value] = True
                    self.mat[i][j].dirs[Dirs.right.value] = True

    def textify(self, path) -> None:
        # just close your eyes
        edges = []
        index = 0
        for i in range(self.h):
            for j in range(self.w):
                if self.mat[i][j].dirs[Dirs.down.value]:
                    c1 = get_c(self.mat[i][j], Dirs.down)
                    c2 = get_c(self.mat[i + 1][j], Dirs.up)
                    cc1 = get_cc(self.mat[i][j], Dirs.down)
                    cc2 = get_cc(self.mat[i + 1][j], Dirs.up)
                    edges.append((index, i * self.w + j, (i + 1) * self.w + j, c1, c2, cc1, cc2, max(abs(i - (self.h - 1) / 2), abs(j - (self.w - 1) / 2)), max(abs(i + 1 - (self.h - 1) / 2), abs(j - (self.w - 1) / 2))))
                    index += 1
                if self.mat[i][j].dirs[Dirs.right.value]:
                    c1 = get_c(self.mat[i][j], Dirs.right)
                    c2 = get_c(self.mat[i][j + 1], Dirs.left)
                    cc1 = get_cc(self.mat[i][j], Dirs.right)
                    cc2 = get_cc(self.mat[i][j + 1], Dirs.left)
                    edges.append((index, i * self.w + j, i * self.w + j + 1, c1, c2, cc1, cc2, max(abs(i - (self.h - 1) / 2), abs(j - (self.w - 1) / 2)), max(abs(i - (self.h - 1) / 2), abs(j + 1 - (self.w - 1) / 2))))
                    index += 1
        cookies = []
        for edge in edges:
            cookies.append((edge[0],edge[1],edge[2], 
                            #next(filter(lambda item: item[1] == edge[1] and item[2] - self.dir_to_val(c1) ==  edge[1] and None == print(edge[1], edge[1] + self.dir_to_val(c1)),  edges), (-1,))[0],
                            #next(filter(lambda item: item[1] - self.dir_to_val(c2) == edge[2] and item[2] ==  edge[2] and None == print(edge[1], edge[1] + self.dir_to_val(cc1)),  edges), (-1,))[0],
                            #next(filter(lambda item: item[1] == edge[1] and item[2] - self.dir_to_val(cc1) == edge[1] and None == print(edge[2], edge[2] + self.dir_to_val(c2)), edges), (-1,))[0],
                            #next(filter(lambda item: item[1] - self.dir_to_val(cc2) == edge[2] and item[2] == edge[2] and None == print(edge[2], edge[2] + self.dir_to_val(cc2)), edges), (-1,))[0]
                            next(filter(lambda item: item[1] == edge[1] + self.dir_to_val(edge[3]) and item[2] == edge[1] or item[2] == edge[1] + self.dir_to_val(edge[3]) and item[1] == edge[1], edges), (-1,))[0],
                            next(filter(lambda item: item[1] == edge[2] + self.dir_to_val(edge[4]) and item[2] == edge[2] or item[2] == edge[2] + self.dir_to_val(edge[4]) and item[1] == edge[2], edges), (-1,))[0],
                            next(filter(lambda item: item[1] == edge[1] + self.dir_to_val(edge[5]) and item[2] == edge[1] or item[2] == edge[1] + self.dir_to_val(edge[5]) and item[1] == edge[1], edges), (-1,))[0],
                            next(filter(lambda item: item[1] == edge[2] + self.dir_to_val(edge[6]) and item[2] == edge[2] or item[2] == edge[2] + self.dir_to_val(edge[6]) and item[1] == edge[2], edges), (-1,))[0],
                            edge[7], edge[8]))
        with open(path, 'w') as file:
            for cookie, edge in zip(cookies, edges):
                #file.write(f"{edge[0]};{edge[1]};{edge[2]};{edge[3]};{edge[4]};{edge[5]};{edge[6]}\n")
                file.write(f"{cookie[0]};{cookie[1]};{cookie[2]};{cookie[3]};{cookie[4]};{cookie[5]};{cookie[6]};{cookie[7]};{cookie[8]}\n")

def get_c(node: Node, start):
    dirs = [Dirs.up, Dirs.right, Dirs.down, Dirs.left]
    off = dirs.index(start)
    dirs = dirs[off:] + dirs[:off]
    dirs = dirs[1:] + [dirs[0]]
    # print(dirs)
    for dir in dirs:
        if node.dirs[dir.value]:
            return dir
        
def get_cc(node: Node, start):
    dirs = [Dirs.up, Dirs.left, Dirs.down, Dirs.right]
    off = dirs.index(start)

    dirs = dirs[off:] + dirs[:off]
    dirs = dirs[1:] + [dirs[0]]
    # print(dirs)
    for dir in dirs:
        if node.dirs[dir.value]:
            return dir

g = Crate(4,4)
g.randomize(0.6)
g.generate()
g.print()
g.textify("./graphs/gen.txt")
