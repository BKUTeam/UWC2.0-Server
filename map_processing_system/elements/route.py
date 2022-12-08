from enum import Enum

from locals import Locals
from map_processing_system.elements.route_node import OptimizeRouteNode
from map_processing_system.directions_api import DirectionsAPI


class OptimizeRoute:
    def __init__(self, list_node: list[OptimizeRouteNode]):
        self.list_node = list_node
        self.render_route = DirectionsAPI.get_distance([node.location for node in list_node])
        self.id = -1

    def get_route_info(self):
        total_loaded_phase_1 = 0
        total_loaded_phase_2 = 0
        distance_phase_1 = 0
        distance_phase_2 = 0

        phase = 1
        for node in self.list_node:
            if node.type == 'FACTORY':
                phase = 2

            if node.type == 'MCP':
                if phase == 1:
                    total_loaded_phase_1 += node.loaded
                    distance_phase_1 += node.reached_distance
                elif phase == 2:
                    total_loaded_phase_2 += node.loaded
                    distance_phase_2 += node.reached_distance

        return {
            'total_loaded_phase_1': total_loaded_phase_1,
            'total_loaded_phase_2': total_loaded_phase_2,
            'distance_phase_1': distance_phase_1,
            'distance_phase_2': distance_phase_2
        }

    def is_valid_route_with_vehicle(self, condition: dict) -> bool:
        """
        This method check a route is valid or not by some condition
        You must add 'vehicle_capacity' field in condition param
        Condition:
         - Check vehicle capacity
         - Check total loaded in each phase is enough or not
        """

        percent_load_in_phase_1 = condition.get('percent_load_in_phase_1')
        percent_load_in_phase_2 = condition.get('percent_load_in_phase_2')
        vehicle_capacity = condition.get('vehicle_capacity')

        if vehicle_capacity is None:
            raise Exception("[is_valid_route] - Not found vehicle capacity in condition")

        route_info = self.get_route_info()

        if percent_load_in_phase_1 is None:
            percent_load_in_phase_1 = Locals.load_config().get('default_loaded_percent')

        if percent_load_in_phase_2 is None:
            percent_load_in_phase_2 = Locals.load_config().get('default_loaded_percent')

        if route_info['total_loaded_phase_1'] > vehicle_capacity or \
                route_info['total_loaded_phase_2'] > vehicle_capacity:
            return False

        if (route_info['total_loaded_phase_1'] >= vehicle_capacity * percent_load_in_phase_1 / 100) and \
                (route_info['total_loaded_phase_2'] >= vehicle_capacity * percent_load_in_phase_2 / 100):
            return True

        return False


class StoredRouteState(Enum):
    ASSIGNED = 'ASSIGNED'
    FREE = 'FREE'
    RELEASED = 'RELEASED'


class StoredRoute:
    ID = -1
    all_routes = []

    def __init__(self, id, depot_id: int, opt_route: OptimizeRoute, type, collector_id=-1):
        self.id = id
        self.opt_route = opt_route
        self.depot_id = depot_id
        self.collector_id: int = collector_id
        self.vehicle_id: int = -1
        self.state: StoredRouteState = StoredRouteState.FREE
        self.type = type

    def __str__(self):
        return f'id: {self.id}\nopt_route: {self.opt_route}\ndepot_id: {self.depot_id}\n' \
               f'collector_id: {self.collector_id}\n' \
               f'vehicle_id: {self.vehicle_id}\nstate: {self.state}\ntype: {self.type}\n'

    def assign_to(self, collector_id: int):
        if self.state != StoredRouteState.FREE or self.collector_id != collector_id:
            raise Exception('Can not assign for this route')

        self.collector_id = collector_id
        self.state = StoredRouteState.ASSIGNED
        StoredRoute.print_all_routes("AFTER ASSIGN")

    def release(self):
        self.state = StoredRouteState.RELEASED
        StoredRoute.print_all_routes("AFTER RELEASE")

    @staticmethod
    def print_all_routes(title):
        print(f"\n\n----------------------------- {title}: Print all route -----------------------------\n")
        for route in StoredRoute.all_routes:
            print(str(route))
            print('---------------------------------\n')
        print("\n---------------------------------------------------------------------------\n\n")

    @staticmethod
    def get_id():
        StoredRoute.ID += 1
        return StoredRoute.ID

    @staticmethod
    def store_route(opt_route: OptimizeRoute, depot_id, type, collector_id=-1):
        """
        This method store route into db and generate id for opt_route
        """
        new_id = StoredRoute.get_id()
        opt_route.id = new_id
        new_stored_route = StoredRoute(new_id, depot_id, opt_route, type, collector_id)
        StoredRoute.all_routes.append(new_stored_route)
        # print("New store route: " + str(new_stored_route))
        StoredRoute.print_all_routes("AFTER STORE")

    @staticmethod
    def get_route_by_id(id):
        for route in StoredRoute.all_routes:
            if route.id == id:
                return route
        return None

    @staticmethod
    def get_free_routes_by_depot_id(depot_id) -> list:
        return [route for route in StoredRoute.all_routes
                if route.depot_id == depot_id and route.state == StoredRouteState.FREE]

    @staticmethod
    def get_assigned_routes_by_depot_id(depot_id):
        return [route.opt_route for route in StoredRoute.all_routes
                if route.depot_id == depot_id and route.state == StoredRouteState.ASSIGNED]

    @staticmethod
    def get_assigned_routes_by_collector_id(collector_id):
        return [route.opt_route for route in StoredRoute.all_routes
                if route.depot_id == collector_id and route.state == StoredRouteState.ASSIGNED]

    @staticmethod
    def get_free_routes_of_collector(collector_id):
        return [route for route in StoredRoute.all_routes
                if route.collector_id == collector_id and route.state == StoredRouteState.FREE]
