from map_processing_system.elements.route import OptimizeRoute, StoredRoute, StoredRouteState
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository


class MapService:

    def __init__(self,
                 map_processing: MapProcessing,
                 map_repository: MapRepository,
                 user_repository: UserRepository) -> None:
        self.map_processing = map_processing
        self.map_repository = map_repository
        self.user_repository = user_repository

    def get_optimize_routes_for_collector(self, collector_id: int, more_route=False):
        collector = self.user_repository.get_collector_by_id(collector_id)
        if collector is None:
            return None
        depot_id = collector['depot_id']
        vehicle_id = collector['vehicle_id']
        free_routes = StoredRoute.get_free_routes_by_depot_id(depot_id)

        if len(free_routes) > 0:
            return free_routes

        if more_route:
            all_routes = self.map_processing.get_more_optimize_routes(depot_id, vehicle_id)
        else:
            all_routes = self.map_processing.get_optimize_routes_of_depot(depot_id)

        for opt_route in all_routes:
            StoredRoute.store_route(opt_route, depot_id, type='ORIGIN' if not more_route else 'OPTIONAL')
        return all_routes

    def assign_route_for_collector(self, route_id, collector_id):
        """
        This method assign route for collector \n
        After assignment, if all collectors of the depot was assigned, release all free routes of the depot
        Or release if type of route is 'OPTIONAL'.

        :param route_id:
        :param collector_id:
        :return: True if success, and vice versa
        """
        route: StoredRoute = StoredRoute.get_route_by_id(route_id)
        if route is None:
            return False
        try:
            route.assign_to(collector_id)
        except Exception as e:
            print(e)
            return False

        depot_id = route.depot_id
        free_routes: list[StoredRoute] = StoredRoute.get_free_routes_by_depot_id(depot_id)
        assigned_routes: list[StoredRoute] = StoredRoute.get_assigned_routes_by_depot_id(depot_id)
        collectors = self.map_repository.get_collectors_of_depot(depot_id)

        if len(collectors) == len(assigned_routes):
            for free_route in free_routes:
                self.release_route(free_route)
        elif route.type == 'OPTIONAL':
            for free_route in free_routes:
                if free_route.type == 'OPTIONAL':
                    self.release_route(free_route)

    def release_route(self, free_route: StoredRoute):
        """
        This method release a route, release Stored Route and release node into MCP Pool of Map Processing.

        :param free_route: StoredRoute has FREE state
        """
        free_route.release()
        self.map_processing.release_redundant_route(free_route.opt_route)

    def simulate_map_data(self):
        depots = self.map_repository.get_all_depots()
        mcps = self.map_repository.get_all_mcps()
        factories = self.map_repository.get_all_factories()
        return depots, mcps, factories

    def get_facility_info(self, facility_type, facility_id):
        #result = []
        if facility_type== 'depot':
            result = self.map_repository.get_depot_by_id(facility_id)
        elif facility_type== 'mcp':
            result=self.map_repository.get_mcp_by_id(facility_id)
        elif facility_type== 'factory':
            result=self.map_repository.get_factory_by_id(facility_id)
        return result


