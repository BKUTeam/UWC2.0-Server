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

    @staticmethod
    def resource(file_path):
        with open(file_path) as f:
            resource = json.load(f)
        return resource

    def get_depot_by_id(self, depot_id):
        for depot in MapRepository.resource(self.depots_path):
            if depot['id'] == depot_id:
                return depot
        return None

    def get_vehicle_by_id(self, vehicle_id):
        for vehicle in MapRepository.resource(self.vehicles_path):
            if vehicle['id'] == vehicle_id:
                return vehicle
        return None

    def get_mcps_of_depot(self, depot_id):
        return [mcp for mcp in MapRepository.resource(self.mcps_path) if mcp['depot_id'] == depot_id]

    def get_vehicles_of_depot(self, depot_id):
        return [vehicle for vehicle in MapRepository.resource(self.vehicles_path) if vehicle['depot_id'] == depot_id]

    def get_all_factories(self):
        return MapRepository.resource(self.factories_path)

    def get_all_depots(self):
        return MapRepository.resource(self.depots_path)

    def get_all_mcps(self):
        return MapRepository.resource(self.mcps_path)

    def get_collectors_of_depot(self, depot_id):
        return [collector for collector in MapRepository.resource(self.collectors_path)
                if collector['depot_id'] == depot_id]
