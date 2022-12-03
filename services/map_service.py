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
        collectors = self.user_repository.get_collectors_of_depot(depot_id)

        if len(collectors) == len(assigned_routes):
            for free_route in free_routes:
                self.release_route(free_route)
        elif route.type == 'OPTIONAL':
            for free_route in free_routes:
                if free_route.type == 'OPTIONAL':
                    self.release_route(free_route)
        return True

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

    # ###### GET ALL mcp, depot, factory
    def get_all_mcps(self):
        return self.map_repository.get_all_mcps()

    def get_all_depots(self):
        return self.map_repository.get_all_depots()

    def get_all_factories(self):
        return self.map_repository.get_all_factories()

    # ###### GET BY ID mcp, depot, factory
    def get_detail_mcp_by_id(self, mcp_id):
        mcp = self.map_repository.get_mcp_by_id(mcp_id)
        return mcp

    def get_detail_depot_by_id(self, depot_id):
        depot = self.map_repository.get_depot_by_id(depot_id)
        mcps_amount = len(self.map_repository.get_mcps_of_depot(depot_id))
        full_mcps_amount = self.map_repository.get_amount_full_mcps_of_depot(depot_id)
        in_route_mcps_amount = self.map_repository.get_amount_in_route_mcps_of_depot(depot_id)
        collector_amount = len(self.user_repository.get_collectors_of_depot(depot_id))
        janitor_amount = len(self.user_repository.get_janitors_of_depot(depot_id))
        vehical_amount = len(self.map_repository.get_vehicles_of_depot(depot_id))
        depot['mcps_amount'] = mcps_amount
        depot['full_mcps_amount'] = full_mcps_amount
        depot['in_route_mcps_amount'] = in_route_mcps_amount
        depot['worker_amount'] = collector_amount + janitor_amount
        depot['collector_amount'] = collector_amount
        depot['janitor_amount'] = janitor_amount
        depot['vehical_amount'] = vehical_amount

        return depot

    def get_detail_factory_by_id(self, factory_id):
        factory = self.map_repository.get_factory_by_id(factory_id)
        return factory

    def get_mcps_of_depot(self, depot_id):
        return self.map_repository.get_mcps_of_depot(depot_id)
