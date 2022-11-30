
class SimpleRouteNode:

    def __init__(self, index, distance, loaded) -> None:
        self.index = index
        self.distance = distance
        self.loaded = loaded


class OptimizeRouteNode:

    def __init__(self, id, location, reached_distance, loaded, type):
        self.object_id = id
        self.location = location
        self.reached_distance = reached_distance
        self.loaded = loaded
        self.type = type

    def __str__(self) -> str:
        return f"id: {self.object_id}\t\t tp: {self.type[:4]}\t\t " \
               f"loc: {' - '.join([str(loc)[:5] for loc in self.location.split(',')])} \t\t " \
               f"dt: {self.reached_distance}\t\t ld: {self.loaded}"
