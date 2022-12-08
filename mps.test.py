import argparse
import json
import sys
from time import time

from map_processing_system.elements.route import OptimizeRoute, StoredRoute
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService
from utils import print_matrix, print_dict
from locals import Locals
from utils import print_scenario, print_stored_routes


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-cid", "--collector_id",
                        type=int,
                        required=False)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    map_repo = MapRepository()
    user_repo = UserRepository()
    map_processing = MapProcessing(map_repository=map_repo)
    map_service = MapService(map_processing, map_repo, user_repo)

    count_route = 0
    count_valid_route = 0

    print_scenario(map_repo, user_repo)

    collectors = []
    if args.collector_id is not None:
        col = user_repo.get_collector_by_id(args.collector_id)
        if col:
            collectors = [col]
    else:
        collectors = user_repo.get_all_collectors()

    if len(collectors) == 0:
        print("Not found collector")
        sys.exit(1)

    start = time()
    for col in collectors:

        routes: list[OptimizeRoute] = map_service.get_optimize_routes_for_collector_v2(collector_id=col['id'])
        print("\n\n--------------------------------- Col id: {} ---------------------------------\n".format(col['id']))
        if isinstance(routes, str):
            print(routes)
        for index, route in enumerate(routes):
            count_route += 1
            route_info = route.get_route_info()
            print(f"Route {index}:")
            print_dict(route_info)

            is_valid_route = route.is_valid_route_with_vehicle(condition={'vehicle_capacity': 4000})
            if is_valid_route:
                count_valid_route += 1
            print(f"Is valid for capacity {4000}: "
                  f" {is_valid_route}")
            for node in route.list_node:
                print('\t', node)

        print("\n-----------------------------------------------------------------------------\n\n")

        print(f"Number of routes: {count_route}")
        print(f"Number of valid routes: {count_valid_route}")
        # print_stored_routes()
        # print(map_processing.mcp_pool)

    end = time()

    time_to_solved = end - start
    print(time_to_solved)
