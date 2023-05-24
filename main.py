from collection import Collection

def main():
    collection = Collection()
    collection.load_file('graphs/Baker.txt')
    collection.materialize()

    collection.create_faces()
    collection.create_spanning_tree()

    finalTable = collection.solve()

    print("Final Table:")
    for k in finalTable.value:
        print(k, finalTable.value[k])

#     print("Proceseed faces:", collection.rootedTree.facesProcessed)
#     root = collection.rootedTree.root
#     printRoot(root)

# def printRoot(root):
#     print((root.u.id, root.v.id) , [(e.u.id, e.v.id) for e in root.children])
#     for child in root.children:
#         printRoot(child)

    # print("Faces:")
    # for face in collection.faces:
    #     print(face.id, [e.id for e in face.edges])

    # print("Spanning Tree:")
    # for vertex in collection.spanningTree.vertices:
    #         print("Face " if vertex.isFace else "Edge ", vertex.data.id, [("F:" if e.isFace else "E:") + str(e.data.id) for e in vertex.neighbors])
    
    # for vertex in collection.vertices.values():
    #     temp = str(vertex.id) + ' -> '
    #     startV = vertex.clockwise_vertices.head
    #     head = startV
    #     while head.next != startV:
    #         temp += str(head.data.id) + ', '
    #         head = head.next
    #     print(temp + str(head.data.id))

    # for vertex in collection.vertices.values():
    #     print(vertex.id, [(e.id, (e.u.id, e.v.id)) for e in vertex.edges])        

if __name__ == '__main__':
    main()
