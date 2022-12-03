from enum import Enum

from map_processing_system.elements.route_node import OptimizeRouteNode


class OptimizeRoute:
    def __init__(self, list_node: list[OptimizeRouteNode]):
        self.list_node = list_node
        self.render_route = ""
        self.id = -1


class StoredRouteState(Enum):
    ASSIGNED = 'ASSIGNED'
    FREE = 'FREE'
    RELEASED = 'RELEASED'


class StoredRoute:

    ID = -1
    all_routes = []

    @staticmethod
    def get_id():
        StoredRoute.ID += 1
        return StoredRoute.ID

    @staticmethod
    def store_route(opt_route: OptimizeRoute, depot_id, type):
        """
        This method store route into db and generate id for opt_route
        """
        new_id = StoredRoute.get_id()
        opt_route.id = new_id
        StoredRoute.all_routes.append(StoredRoute(new_id, depot_id, opt_route, type))

    @staticmethod
    def get_route_by_id(id):
        for route in StoredRoute.all_routes:
            if route.id == id:
                return route
        return None

    @staticmethod
    def get_free_routes_by_depot_id(depot_id) -> list:
        return [route.opt_route for route in StoredRoute.all_routes
                if route.depot_id == depot_id and route.state == StoredRouteState.FREE]

    def __init__(self, id, depot_id: int, opt_route: OptimizeRoute, type):
        self.id = id
        self.opt_route = opt_route
        self.depot_id = depot_id
        self.collector_id: int = -1
        self.vehicle_id: int = -1
        self.state: StoredRouteState = StoredRouteState.FREE
        self.type = type

    def assign_to(self, collector_id: int):
        if self.state != StoredRouteState.FREE:
            raise Exception('Can not assign for this route')

        self.collector_id = collector_id
        self.state = StoredRouteState.ASSIGNED

    def release(self):
        self.state = StoredRouteState.RELEASED

    @staticmethod
    def get_assigned_routes_by_depot_id(depot_id):
        return [route.opt_route for route in StoredRoute.all_routes
                if route.depot_id == depot_id and route.state == StoredRouteState.ASSIGNED]

