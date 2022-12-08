from map_processing_system.elements.route import OptimizeRoute, StoredRoute, StoredRouteState
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
import traceback

class MapService:

    def __init__(self,
                 map_processing: MapProcessing,
                 map_repository: MapRepository,
                 user_repository: UserRepository) -> None:
        self.map_processing = map_processing
        self.map_repository = map_repository
        self.user_repository = user_repository

    # ###### Route involved method
    def get_optimize_routes_for_collector_v2(self, collector_id: int, more_route=False):
        try:
            collector = self.user_repository.get_collector_by_id(collector_id)

            if not collector:
                return "Not found this collector"

            if collector.get('state') == 'BUSY':
                return "The collector already has assigned route"

            depot_id = collector['depot_id']
            vehicle_id = collector['vehicle_id']

            if more_route:
                # Use mcp pool here
                vehicle = self.map_repository.get_vehicle_by_id(vehicle_id)
                vehicle_capacities = [vehicle['capacity']] * 2
                all_routes = self.map_processing.get_more_optimize_routes(depot_id, vehicle_capacities)
            else:
                # Return available route in last request
                routes = StoredRoute.get_free_routes_of_collector(collector_id)
                if len(routes) > 0:
                    return [route.opt_route for route in routes]

                vehicle = self.map_repository.get_vehicle_by_id(vehicle_id)
                vehicle_capacities = [vehicle['capacity']] * 2
                all_routes = self.map_processing.get_optimize_routes_of_depot(depot_id, vehicle_capacities)

            for opt_route in all_routes:
                StoredRoute.store_route(opt_route, depot_id, ('ORIGIN' if not more_route else 'OPTIONAL'), collector_id)

            return all_routes

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print(ex, traceback.format_exc())
            return message

    def assign_route_for_collector_v2(self, route_id, collector_id):
        """
        This method assign route for collector \n
        After assignment, release all another route of the collector

        :param route_id:
        :param collector_id:
        :return: True if success, and vice versa
        """
        try:
            collector = self.user_repository.get_collector_by_id(collector_id)

            if not collector:
                return "Not found this collector"

            if collector.get('state') == 'BUSY':
                return "The collector already has assigned route"

            route: StoredRoute = StoredRoute.get_route_by_id(route_id)
            if route is None:
                return False

            route.assign_to(collector_id)

            self.map_processing.update_mcp_state_in_route(route.opt_route)
            self.user_repository.update_state_of_collector(collector_id, 'BUSY')

            routes = StoredRoute.get_free_routes_by_depot_id(collector['depot_id'])
            for route in routes:
                if route.id != route_id:
                    self.release_route_v2(route)

            # Check all collectors have routes -> update MCP pool if true
            collectors_in_depot = self.map_repository.get_collectors_of_depot(depot_id=collector['depot_id'])
            assigned_routes = StoredRoute.get_assigned_routes_by_depot_id(collector['depot_id'])
            if len(assigned_routes) == len(collectors_in_depot):
                self.map_processing.merge_pool_from_depot(collector['depot_id'])

            return True
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            print(ex, traceback.format_exc())
            return False

    def release_route_v2(self, free_route: StoredRoute):
        """
        This method release a route, release Stored Route and release node into MCP Pool of Map Processing.

        :param free_route: StoredRoute has FREE state
        """
        free_route.release()
        # self.map_processing.release_redundant_route(free_route.opt_route)

    # ###### GET ALL mcp, depot, factory
    def get_all_mcps(self):
        return self.map_repository.get_all_mcps()

    def get_all_depots(self):
        return self.map_repository.get_all_depots()

    def get_all_factories(self):
        return self.map_repository.get_all_factories()

    # ###### GET BY ID mcp, depot, factory
    def get_detail_mcp_by_id(self, mcp_id):
        return self.map_repository.get_mcp_by_id(mcp_id)

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
        return self.map_repository.get_factory_by_id(factory_id)

    def get_mcps_of_depot(self, depot_id):
        return self.map_repository.get_mcps_of_depot(depot_id)
