import json
from time import time

from map_processing_system.elements.route import OptimizeRoute, StoredRoute
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService
from utils import print_matrix, print_dict
from locals import Locals


def print_stored_routes():
    print("\n--------------------------------- Stored route ---------------------------------\n")
    st_routes: list[StoredRoute] = StoredRoute.all_routes
    for i, st_route in enumerate(st_routes):
        print(" {}: type - {}, state - {} _____".format(i, st_route.type, st_route.state))
        print(" Collector id: {}, depot id: {}".format(st_route.collector_id, st_route.depot_id))
        for node in st_route.opt_route.list_node:
            print('\t', node)
    print("\n--------------------------------- Stored route ---------------------------------\n\n")


def print_scenario(map_repo: MapRepository, user_repo: UserRepository):
    depots = map_repo.get_all_depots()

    mcp_filled_threshold = Locals.load_config()['mcp_filled_threshold']
    print("\n\n--------------------------------- UWC 2.0 Scenario ---------------------------------\n")
    print(f"MCP filled threshold: {mcp_filled_threshold}%")

    for depot in depots:
        mcps = map_repo.get_mcps_of_depot(depot['id'])
        mcps_exceed_threshold = [
            mcp for mcp in mcps if mcp['filled'] > mcp_filled_threshold
        ]
        print(f"Depot {depot['id']}")
        print(f"\tMCP: ")
        print(f"\t\tNumber of MCPs: {len(mcps)}")
        print(f"\t\tTotal filled of all MCPs: {sum(mcp['capacity'] * mcp['filled'] / 100 for mcp in mcps)}")
        print(f"\t\tNumber of MCPs exceed filled threshold: {len(mcps_exceed_threshold)}")
        print(f"\t\tTotal filled of exceeded MCPs: "
              f"{sum(mcp['capacity'] * mcp['filled'] / 100 for mcp in mcps_exceed_threshold)}")

    print("\n--------------------------------- UWC 2.0 Scenario ---------------------------------\n\n")


if __name__ == "__main__":
    map_repo = MapRepository()
    user_repo = UserRepository()
    map_processing = MapProcessing(map_repository=map_repo)
    map_service = MapService(map_processing, map_repo, user_repo)

    collectors = user_repo.get_all_collectors()

    print_scenario(map_repo, user_repo)

    start = time()
    for col in collectors:
        if col['id'] != 17:
            continue
        routes: list[OptimizeRoute] = map_service.get_optimize_routes_for_collector(collector_id=col['id'])
        print("\n--------------------------------- Col id: {} ---------------------------------\n".format(col['id']))
        for index, route in enumerate(routes):
            route_info = route.get_route_info()
            print(f"Route {index}:")
            print_dict(route_info)
            print(f"Is valid for capacity {4000}: "
                  f" {route.is_valid_route_with_vehicle(condition={'vehicle_capacity': 4000})}")
            for node in route.list_node:
                print('\t', node)

        print("\n------------------------------------------------------------------\n\n")

        print_stored_routes()
        print(map_processing.mcp_pool)

    end = time()

    time_to_solved = end - start
    print(time_to_solved)


