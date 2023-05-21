from collection import Collection

def main():
    collection = Collection()
    collection.load_file('graphs/Baker.txt')
    collection.materialize()

    collection.create_faces()
    
    print("Faces:")
    for face in collection.faces:
        print([e.id for e in face.edges])

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
