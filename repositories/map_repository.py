import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))


class MapRepository:

    def __init__(self) -> None:
        self.mcps_path = os.path.join(root_dir, '../data/mcps.JSON')
        self.vehicles_path = os.path.join(root_dir, '../data/vehicles.JSON')
        self.depots_path = os.path.join(root_dir, '../data/depots.JSON')
        self.factories_path = os.path.join(root_dir, '../data/factories.JSON')
        self.collectors_path = os.path.join(root_dir, '../data/collectors.JSON')
        self.janitors_path = os.path.join(root_dir, '../data/janitors.JSON')

    @staticmethod
    def resource(file_path):
        with open(file_path) as f:
            resource = json.load(f)
        return resource

    # ###### GET ALL
    def get_all_factories(self):
        return MapRepository.resource(self.factories_path)

    def get_all_depots(self):
        return MapRepository.resource(self.depots_path)

    def get_all_mcps(self):
        return MapRepository.resource(self.mcps_path)

    # ###### GET BY ID
    def get_mcp_by_id(self, mcp_id):
        for mcp in MapRepository.resource(self.mcps_path):
            if mcp['id'] == mcp_id:
                return mcp
        return None

    def get_factory_by_id(self, factory_id):
        for factory in MapRepository.resource(self.factories_path):
            if factory.get('id') == factory_id:
                return factory
        return None

    def get_depot_by_id(self, depot_id):
        for depot in MapRepository.resource(self.depots_path):
            if depot.get('id') == depot_id:
                return depot
        return None

    def get_vehicle_by_id(self, vehicle_id):
        for vehicle in MapRepository.resource(self.vehicles_path):
            if vehicle.get('id') == vehicle_id:
                return vehicle
        return None

    # ###### GET BY DEPOT ID - get resource at depot
    def get_mcps_of_depot(self, depot_id, filled_threshold=0):
        return [mcp for mcp in MapRepository.resource(self.mcps_path)
                if mcp['depot_id'] == depot_id and mcp['filled'] > filled_threshold]

    def get_collectors_of_depot(self, depot_id):
        return [collector for collector in MapRepository.resource(self.collectors_path)
                if collector['depot_id'] == depot_id]

    def get_vehicles_of_depot(self, depot_id):
        return [vehicle for vehicle in MapRepository.resource(self.vehicles_path) if vehicle['depot_id'] == depot_id]

    def get_amount_full_mcps_of_depot(self, depot_id):
        return len([mcp for mcp in MapRepository.resource(self.mcps_path) if
                    mcp['depot_id'] == depot_id and mcp['state'] == "FULL"])

    def get_amount_in_route_mcps_of_depot(self, depot_id):
        return len([mcp for mcp in MapRepository.resource(self.mcps_path) if
                    mcp['depot_id'] == depot_id and mcp['state'] == "IN_ROUTE"])

    # ###### UPDATE data method
    def update_mcp_in_route(self, mcps_id):
        mcps = MapRepository.resource(self.mcps_path)
        for mcp_id in mcps_id:
            for mcp in mcps:
                if mcp.get('id') == mcp_id:
                    mcp['state'] = "IN_ROUTE"
                    break
        with open(self.mcps_path, 'w+') as f:
            json.dump(mcps, f, indent=2)
        return True

