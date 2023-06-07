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

    T = collection.solve()
    if T is not None:
        T.print()
    else:
        print("No solution")

if __name__ == '__main__':
    main()
