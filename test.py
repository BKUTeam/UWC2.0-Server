from map_processing_system.elements.route import OptimizeRoute, StoredRoute
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService
from utils import print_matrix


def print_stored_routes():
    print("_________________ Stored route _________________________")
    st_routes: list[StoredRoute] = StoredRoute.all_routes
    for i, st_route in enumerate(st_routes):
        print(" _____ {}: type - {}, state - {} _____".format(i, st_route.type, st_route.state))
        print(" _____ Collector id: {}, depot id: {}".format(st_route.collector_id, st_route.depot_id))
        for node in st_route.opt_route.list_node:
            print('\t', node)


if __name__ == "__main__":
    map_repo = MapRepository()
    user_repo = UserRepository()
    map_processing = MapProcessing(map_repository=map_repo)
    map_service = MapService(map_processing, map_repo, user_repo)

    routes: list[OptimizeRoute] = map_service.get_optimize_routes_for_collector(collector_id=13)
    for index, route in enumerate(routes):
        print(f"Route {index}:")
        for node in route.list_node:
            print('\t', node)

    # map_service.assign_route_for_collector(collector_id=13, route_id=0)
    # map_service.assign_route_for_collector(collector_id=18, route_id=0)
    print_stored_routes()
    print(map_processing.mcp_pool)
