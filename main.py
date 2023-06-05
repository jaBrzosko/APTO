from collection import Collection

def main():
    collection = Collection()
    collection.load_file('graphs/twoSecondLayers.txt')
    collection.materialize()
    collection.reverse_layers()

    collection.make_layers()
    collection.split_layers()

    collection.traingulate()
    collection.materialize()

    collection.materialize_faces()
    collection.create_layers_faces()
    collection.check_reversing()
    collection.create_layers_spanning_trees()
    collection.find_encloseres()
    collection.calculate_lbrb()

    for i, layer in enumerate(collection.layers):
        print("Layer", i)
        # for vertex in layer.vertices.values():
            # print(vertex.id, vertex.layer, [v.id for v in vertex.fatherCollection.vertices.values()])
        # for face in layer.faces:
            # print(face.id, [e.id for e in face.edges])
        # for vertex in layer.spanningTree.vertices:
            # print("Face " if vertex.isFace else "Edge ", vertex.data.id, [("F:" if e.isFace else "E:") + str(e.data.id) for e in vertex.neighbors])
        root = layer.rootedTree.root
        printRoot(root)

    # for layer in collection.layers.values():
    #     layer.materialize()
    #     for vertex in layer.vertices.values():
    #         temp = str(vertex.id) + ' layer: ' + str(vertex.layer) + ' -> '
    #         startV = vertex.clockwise_vertices.head
    #         head = startV
    #         while head.next != startV:
    #             temp += str(head.data.id) + ', '
    #             head = head.next

    #         temp += str(head.data.id) + ' -> '
    #         startV = vertex.counterclockwise_vertices.head
    #         head = startV
    #         while head.next != startV:
    #             temp += str(head.data.id) + ', '
    #             head = head.next
    #         print(temp + str(head.data.id))

    # collection.create_faces()
    # collection.create_spanning_tree()

    # finalTable = collection.solve()

    # print("Final Table:")
    # for k in finalTable.value:
    #     print(k, finalTable.value[k])

#     print("Proceseed faces:", collection.rootedTree.facesProcessed)
#     root = collection.rootedTree.root
#     printRoot(root)

    # print("Faces:")
    # for face in collection.faces:
    #     print(face.id, [e.id for e in face.edges])

    # print("Spanning Tree:")
    # for vertex in collection.spanningTree.vertices:
    #         print("Face " if vertex.isFace else "Edge ", vertex.data.id, [("F:" if e.isFace else "E:") + str(e.data.id) for e in vertex.neighbors])
    
    # for vertex in collection.vertices.values():
    #     temp = str(vertex.id) + ' layer: ' + str(vertex.layer) + ' -> '
    #     startV = vertex.clockwise_vertices.head
    #     head = startV
    #     while head.next != startV:
    #         temp += str(head.data.id) + ', '
    #         head = head.next

    #     temp += str(head.data.id) + ' -> '
    #     startV = vertex.counterclockwise_vertices.head
    #     head = startV
    #     while head.next != startV:
    #         temp += str(head.data.id) + ', '
    #         head = head.next
    #     print(temp + str(head.data.id))

    # for vertex in collection.vertices.values():
    #     print(vertex.id, [(e.id, (e.u.id, e.v.id)) for e in vertex.edges])        

def printRoot(root):
    if root.u.layer != 0:
        leftBoundary, rightBoundary = root.getBoundaries()
        if leftBoundary is None or rightBoundary is None:
            print("No boundaries")
        else:
            print("Boundaries:", [v.id for v in leftBoundary], [v.id for v in rightBoundary])
    print((root.u.id, root.v.id), (root.lb, root.rb), [(e.u.id, e.v.id) for e in root.children]) #, None if root.enclosingFaceRoot is None else (root.enclosingFaceRoot.u.id, root.enclosingFaceRoot.v.id))
    # print((root.u.id, root.v.id) , [(e.u.id, e.v.id) for e in root.children], 
        #   "No encloser" if root.enclosingFaceRoot is None else (root.enclosingFaceRoot.u.id, root.enclosingFaceRoot.v.id),
        #   "No enclosing" if len(root.enclosedComponents) == 0 else [(e.rootedTree.root.u.id, e.rootedTree.root.v.id) for e in root.enclosedComponents])
    for child in root.children:
        printRoot(child)

if __name__ == '__main__':
    main()
