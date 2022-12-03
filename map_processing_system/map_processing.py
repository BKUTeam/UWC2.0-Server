import json

from map_processing_system.elements.route import OptimizeRoute
from map_processing_system.elements.route_node import OptimizeRouteNode
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.or_tools import VRPSolve
from repositories.map_repository import MapRepository
from utils import print_matrix

DEFAULT_FILLED = 0


class MapProcessing:
    NOT_MOVE_DISTANCE = 1000000000 - 1
    DEFAULT_FILLED = 0

    def __init__(self, map_repository: MapRepository):
        self.map_repo = map_repository
        self.mcp_pool: list[int] = []
        self.working_mcps: list = []

    # Helper method below

    def release_redundant_route(self, route: OptimizeRoute):
        for node in route.list_node:
            if node.type == 'MCP':
                self.mcp_pool.append(node.object_id)

    def set_up_working_mcp(self, depot_id):
        mcps = self.map_repo.get_mcps_of_depot(depot_id)
        self.working_mcps = [mcp for mcp in mcps
                             if ('filled' in mcp) and (mcp['filled'] >= DEFAULT_FILLED) and mcp['state'] != 'IN_ROUTE']

    def clear_working_mcps(self):
        self.working_mcps = []

    def merge_pool_to_working_mcp(self):
        mcps = self.map_repo.get_all_mcps()
        self.working_mcps.append([mcp for mcp in mcps if mcp['id'] in self.mcp_pool])

    def get_list_id(self, list_node):
        return [node['id'] for node in list_node]

    def get_list_gg_location(self, list_node):
        return [node['gg_location'] for node in list_node]

    def get_list_capacity(self, list_node):
        return [(int(node['capacity'] * node['filled'] / 100) if ('capacity' in node and 'filled' in node)
                 else
                 (int(node['capacity']) if 'capacity' in node else 0))
                for node in list_node]

    def merge_routes(self, routes_p1, routes_p2, list_location, list_id) -> list[list[OptimizeRouteNode]] | None:

        if len(routes_p1) != len(routes_p2):
            return None

        all_routes = []
        num_routes = len(routes_p1)
        for i in range(num_routes):
            merged_route = []

            # create optimize route node from simple at phrase 1
            route = routes_p1[i]
            for index, node in enumerate(route):
                merged_route.append(
                    OptimizeRouteNode(
                        id=list_id[node.index],
                        location=list_location[node.index],
                        reached_distance=node.distance,
                        loaded=node.loaded,
                        type='DEPOT' if index == 0 else ('FACTORY' if index == len(route) - 1 else 'MCP')
                    )
                )

            # create optimize route node from simple at phrase 1
            route = routes_p2[i]
            for index, node in enumerate(route):
                if index == 0:
                    continue
                merged_route.append(
                    OptimizeRouteNode(
                        id=list_id[node.index],
                        location=list_location[node.index],
                        reached_distance=node.distance,
                        loaded=node.loaded,
                        type='FACTORY' if index == len(route) - 1 else 'MCP'
                    )
                )

            # comeback to depot by the first id
            depot_id = list_id[0]
            depot = self.map_repo.get_depot_by_id(depot_id)
            merged_route.append(
                OptimizeRouteNode(
                    id=depot_id,
                    location=depot['gg_location'],
                    reached_distance=0,
                    loaded=0,
                    type='DEPOT'
                )
            )

            # merge route to list route
            all_routes.append(merged_route)

        return all_routes

    def handle_result_of_first_phrase(self, result_phrase_1, demand_all_nodes):
        """
        Handle result in phrase 1 to find route phrase 2
        -> get valid index of factories where vehicle was in
        -> release demand of loaded

        :param result_phrase_1: solution from the first phrase of routing
        :param demand_all_nodes: demands (capacity) of all node (depot, mcps, factories)
        :return: tuple(factory_indexes_of_factories, loaded_mcp_indexes_in_demands)
        """
        factories = self.map_repo.get_all_factories()
        # Set up for the second phrase: from factories to factories
        factory_indexes_of_factories = []
        loaded_mcp_indexes_in_demands = []
        for route in result_phrase_1:
            for index, node in enumerate(route):
                # last index is index of factory, this index need to reset
                # because factory indexes are duplicated in phrase 1 to compute routes
                if index == len(route) - 1:
                    offset = len(self.working_mcps) + 1  # offset mcps and depot
                    new_factory_index = (index - offset) % len(factories) + offset
                    node.index = new_factory_index  # update to valid index
                    factory_indexes_of_factories.append(new_factory_index)
                else:
                    if node.index > 0:
                        loaded_mcp_indexes_in_demands.append(node.index)
                    demand_all_nodes[node.index] = 0
        return factory_indexes_of_factories, loaded_mcp_indexes_in_demands

    # Main method below

    def get_optimize_routes_from_depot_to_factories(self, original_distance_matrix: list[list[int]],
                                                    demands: list[int], vehicles: list[int]):
        factories = self.map_repo.get_all_factories()
        data = {
            'distance_matrix': original_distance_matrix,
            'demands': demands,
            'vehicle_capacities': vehicles,
            'num_vehicles': len(vehicles),
            'depot': 0
        }

        # set distance from all factories to depot = 0,
        # this mean that we use arbitrary endpoints are factories
        # Problem: vehicle may return to depot without move over any factories
        #  -> when vehicle is fulfilled, distance to depot < distance to any factories
        # Problem solved: or tools prefer to get more node than short distance
        for i in range(len(original_distance_matrix) - len(factories), len(original_distance_matrix)):
            data['distance_matrix'][i][0] = 0

        # duplicate the factories -> one factory can be move over by any vehicles
        new_rows = []
        for index, row in enumerate(data['distance_matrix']):
            if index >= len(data['distance_matrix']) - len(factories):
                # Restrict moving between factories
                data['distance_matrix'][index] \
                    = [0] + [MapProcessing.NOT_MOVE_DISTANCE] * (
                        len(row) - 1 + len(factories) * (data['num_vehicles'] - 1))
                new_rows.append(data['distance_matrix'][index])
            else:
                row += row[-len(factories):] * (data['num_vehicles'] - 1)

        data['distance_matrix'] += new_rows
        data['demands'] += data['demands'][-len(factories):] * (data['num_vehicles'] - 1)

        optimize_routes = VRPSolve(option='basic', data=data)
        return optimize_routes

    def get_optimize_routes_from_factories_to_depot(self, original_distance_matrix: list[list[int]],
                                                    demands: list[int], vehicles: list[int],
                                                    factory_indexes_of_factories, loaded_mcp_indexes_in_demands):
        data = {
            'distance_matrix': original_distance_matrix,
            'demands': demands,
            'vehicle_capacities': vehicles,
            'num_vehicles': len(vehicles),
            'starts': factory_indexes_of_factories,
            'ends': factory_indexes_of_factories
        }

        for i in loaded_mcp_indexes_in_demands:
            for j in range(len(data['distance_matrix'])):
                # Restrict moving to all mcps in the first phrase
                data['distance_matrix'][i][j] = MapProcessing.NOT_MOVE_DISTANCE
                data['distance_matrix'][j][i] = MapProcessing.NOT_MOVE_DISTANCE

        optimize_routes = VRPSolve(option='multi', data=data)
        return optimize_routes

    def get_optimize_routes(self, depot, vehicles):
        factories = self.map_repo.get_all_factories()
        list_node = [depot] + [mcp for mcp in self.working_mcps] + [factory for factory in factories]

        # set up data to use or tools
        list_location = self.get_list_gg_location(list_node)
        list_id = self.get_list_id(list_node)
        demand_all_nodes = self.get_list_capacity(list_node)
        vehicle_capacities = self.get_list_capacity(vehicles)

        result_phrase_1 = self.get_optimize_routes_from_depot_to_factories(
            DirectionsAPI.get_distance_matrix(list_location, list_id),
            demand_all_nodes[:],
            vehicle_capacities[:],
        )

        # handle result in phrase 1 to find route phrase 2
        factory_indexes_of_factories, loaded_mcp_indexes_in_demands \
            = self.handle_result_of_first_phrase(result_phrase_1, demand_all_nodes)

        result_phrase_2 = self.get_optimize_routes_from_factories_to_depot(
            DirectionsAPI.get_distance_matrix(list_location, list_id),
            demand_all_nodes[:],
            vehicle_capacities[:],
            factory_indexes_of_factories[:],
            loaded_mcp_indexes_in_demands[:]
        )

        list_merged_route = self.merge_routes(result_phrase_1, result_phrase_2, list_location, list_id)
        if list_merged_route is None:
            print("Merge routes failure!")

        list_optimize_route = []
        for index, merged_route in enumerate(list_merged_route):
            opt_route = OptimizeRoute(merged_route)
            print(opt_route)
            list_optimize_route.append(opt_route)
        return list_optimize_route

    def get_optimize_routes_of_depot(self, depot_id: int):
        depot = self.map_repo.get_depot_by_id(depot_id)
        vehicles = self.map_repo.get_vehicles_of_depot(depot_id)
        self.set_up_working_mcp(depot_id)
        return self.get_optimize_routes(depot, vehicles)

    def get_more_optimize_routes(self, depot_id, vehicle_id):
        self.set_up_working_mcp(depot_id)
        self.merge_pool_to_working_mcp()
        vehicles = [self.map_repo.get_vehicle_by_id(vehicle_id)]
        if vehicles[0] is None:
            return None
        else:
            vehicles *= 3
        optimize_routes = self.get_optimize_routes(depot_id, vehicles)

        # update pool
        picked_mcps = []
        for route in optimize_routes:
            for node in route.list_node:
                if node.type == 'MCP':
                    picked_mcps.append(node.object_id)
        self.mcp_pool = [mcp_id for mcp_id in self.mcp_pool if mcp_id in picked_mcps]

        return optimize_routes