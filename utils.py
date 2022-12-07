import json

from locals import Locals
from map_processing_system.elements.route import StoredRoute
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository


def export_matrix_str_to_json(_matrix, _filename):
    rows = _matrix.split('\n')
    distance_matrix = [row.split("	") for row in rows]
    for i in range(0, len(distance_matrix)):
        for j in range(0, len(distance_matrix[0])):
            distance_matrix[i][j] = int(distance_matrix[i][j])

    with open("./data/{}".format(_filename), 'w') as wf:
        json.dump(distance_matrix, wf)


def print_matrix(_matrix):
    for i in _matrix:
        print('\t'.join(map(str, i)))


def print_dict(_dict):
    for k, v in _dict.items():
        print(f'{k}: {v}')


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
