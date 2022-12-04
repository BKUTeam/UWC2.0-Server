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

    def get_mcp_by_id(self, mcp_id):
        for mcp in MapRepository.resource(self.mcps_path):
            if mcp['id'] == mcp_id:
                return mcp
        return None

    def get_factory_by_id(self, factory_id):
        for factory in MapRepository.resource(self.factories_path):
            if factory['id'] == factory_id:
                return factory
        return None

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

    # def get_collectors_of_depot(self, depot_id):
    #     return [collector for collector in MapRepository.resource(self.collectors_path)
    #             if collector['depot_id'] == depot_id]
    #
    # # def get_all_collectors(self):
    # #     return MapRepository.resource(self.collectors_path)
    #
    # def get_all_janitors(self):
    #     return MapRepository.resource(self.janitors_path)
    #
    # # def get_detail_collector_by_id(self, collector_id):
    # #     collectors = MapRepository.resource(self.collectors_path)
    # #     for collector in collectors:
    # #         if collector_id == collector.get('id'):
    # #             return collector
    # #
    # #     return ""
    #
    # def get_detail_janitor_by_id(self, janitor_id):
    #     pass

    def get_detail_depot_by_id(self, depot_id):
        depots = MapRepository.resource(self.depots_path)
        for depot in depots:
            if depot_id == depot.get('id'):
                return depot

        return ""

    def get_detail_mcp_by_id(self, mcp_id):
        mcps = MapRepository.resource(self.mcps_path)
        for mcp in mcps:
            if mcp_id == mcp.get('id'):
                return mcp

        return ""
