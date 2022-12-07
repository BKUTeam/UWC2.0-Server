import json

from map_processing_system.elements.route import OptimizeRoute
from map_processing_system.elements.route_node import OptimizeRouteNode
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.or_tools import VRPSolve
from repositories.map_repository import MapRepository
from uwc_logging import UwcLogger
from locals import Locals


class MapProcessing:
    NOT_MOVE_DISTANCE = 999999999999 + 1

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
                             if ('filled' in mcp) and (mcp['filled'] >= Locals.load_config()['mcp_filled_threshold'])
                             and mcp['state'] != 'IN_ROUTE']

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

    def merge_routes(self, routes_p1, routes_p2, list_node_p1, list_node_p2) \
            -> list[list[OptimizeRouteNode]] | None:

        if len(routes_p1) != len(routes_p2):
            return None

        all_routes = []
        num_routes = len(routes_p1)
        for i in range(num_routes):
            merged_route = []

            # create optimize route node from simple at phase 1
            route = routes_p1[i]
            list_location_1 = self.get_list_gg_location(list_node_p1)
            list_id_1 = self.get_list_id(list_node_p1)

            for index, node in enumerate(route):
                merged_route.append(
                    OptimizeRouteNode(
                        id=list_id_1[node.index],
                        location=list_location_1[node.index],
                        reached_distance=node.distance,
                        loaded=node.loaded,
                        type=list_node_p1[node.index]['type']
                    )
                )

            # create optimize route node from simple at phase 1
            route = routes_p2[i]
            list_location_2 = self.get_list_gg_location(list_node_p2)
            list_id_2 = self.get_list_id(list_node_p2)
            for index, node in enumerate(route):
                if index == 0:
                    continue
                merged_route.append(
                    OptimizeRouteNode(
                        id=list_id_2[node.index],
                        location=list_location_2[node.index],
                        reached_distance=node.distance,
                        loaded=node.loaded,
                        type=list_node_p2[node.index]['type']
                    )
                )

            depot = list_node_p1[0]
            factory = merged_route[len(merged_route) - 1]
            merged_route.append(
                OptimizeRouteNode(
                    id=depot['id'],
                    location=depot['gg_location'],
                    reached_distance=DirectionsAPI.get_distance([factory.location, depot['gg_location']]),
                    loaded=0,
                    type=depot['type']
                )
            )

            # merge route to list route
            all_routes.append(merged_route)

        return all_routes

    def get_list_node_for_next_phase(self, routes, list_node):
        """
        Handle result in phase 1 to get list node for phase 2

        :param routes: all routes from the first phase
        :param list_node: all nodes are used in the first phase
        :return: new_list_node
        """
        offset = 0
        for node in list_node:
            if node['type'] != 'FACTORY':
                offset += 1
        num_factories = len(list_node) - offset

        list_mcps = []
        list_factories = []
        for route in routes:
            for index, node in enumerate(route):
                if index == 0:
                    # not use depot in next phase
                    continue
                elif index == len(route) - 1:
                    node.index = (node.index - offset) % num_factories + offset
                    list_factories.append(list_node[node.index])
                else:
                    # Mcp here
                    list_mcps.append(list_node[node.index])

        return list_mcps + list_factories

    # Main method below

    def get_optimize_routes_from_depot_to_factories(self, distance_matrix: list[list[int]],
                                                    demands: list[int], vehicles: list[int]):
        factories = self.map_repo.get_all_factories()
        data = {
            'distance_matrix': distance_matrix,
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
        for i in range(len(distance_matrix) - len(factories), len(distance_matrix)):
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

    def get_optimize_routes_from_factories_to_depot(self, distance_matrix: list[list[int]],
                                                    demands: list[int], vehicles: list[int],
                                                    index_of_factories):
        data = {
            'distance_matrix': distance_matrix,
            'demands': demands,
            'vehicle_capacities': vehicles,
            'num_vehicles': len(vehicles),
            'starts': index_of_factories,
            'ends': index_of_factories
        }

        optimize_routes = VRPSolve(option='multi', data=data)
        return optimize_routes

    def get_optimize_routes(self, depot, vehicles):
        factories = self.map_repo.get_all_factories()

        depot['type'] = 'DEPOT'
        list_node_1 = [depot]
        for mcp in self.working_mcps:
            mcp['type'] = 'MCP'
            list_node_1.append(mcp)
        for factory in factories:
            factory['type'] = 'FACTORY'
            list_node_1.append(factory)

        # set up data to use or tools in the first phase
        list_location = self.get_list_gg_location(list_node_1)
        list_id = self.get_list_id(list_node_1)
        demand_all_nodes = self.get_list_capacity(list_node_1)
        vehicle_capacities = self.get_list_capacity(vehicles)

        result_phase_1 = self.get_optimize_routes_from_depot_to_factories(
            DirectionsAPI.get_distance_matrix(list_location, list_id, 'phase1'),
            demand_all_nodes[:],
            vehicle_capacities[:],
        )

        # handle result in phase 1 to find route phase 2
        new_list_node = self.get_list_node_for_next_phase(result_phase_1, list_node_1)
        list_location = self.get_list_gg_location(new_list_node)
        list_id = self.get_list_id(new_list_node)
        demand_all_nodes = self.get_list_capacity(new_list_node)

        index_of_factories = []
        for index, node in enumerate(new_list_node):
            if node['type'] == 'FACTORY':
                index_of_factories.append(index)

        result_phase_2 = self.get_optimize_routes_from_factories_to_depot(
            DirectionsAPI.get_distance_matrix(list_location, list_id, 'phase2'),
            demands=demand_all_nodes[:],
            vehicles=vehicle_capacities[:],
            index_of_factories=index_of_factories,
        )

        list_merged_route = self.merge_routes(result_phase_1, result_phase_2, list_node_1, new_list_node)
        if list_merged_route is None:
            print("Merge routes failure!")

        list_optimize_route = []
        for index, merged_route in enumerate(list_merged_route):
            opt_route = OptimizeRoute(merged_route)
            list_optimize_route.append(opt_route)
        return list_optimize_route

    def get_optimize_routes_of_depot(self, depot_id: int):
        depot = self.map_repo.get_depot_by_id(depot_id)
        vehicles = self.map_repo.get_vehicles_of_depot(depot_id)
        self.set_up_working_mcp(depot_id)
        return self.get_optimize_routes(depot, vehicles)

    def get_more_optimize_routes(self, depot_id, vehicle_id):
        self.set_up_working_mcp(depot_id)

        UwcLogger.add_info_log("MCP Pool", "Using mcp pool, previous length: {}".format(len(self.mcp_pool)))
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

    def update_mcp_state_in_route(self, route):
        picked_mcps = []
        for node in route.list_node:
            if node.type == 'MCP':
                picked_mcps.append(node.object_id)
        self.map_repo.update_mcp_in_route(picked_mcps)

        return "success"
