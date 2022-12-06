from map_processing_system.elements.route import OptimizeRoute, StoredRoute, StoredRouteState
from repositories.user_repository import UserRepository


class UserService:

    def __init__(self,
                 user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    # ###### UPDATE data method
    def assign_mcp_to_janitor(self, mcp_id, janitor_id):
        return self.user_repository.save_mcp_for_janitor(janitor_id, mcp_id)

    def assign_depot_to_janitor(self, depot_id, janitor_id):
        return self.user_repository.save_depot_for_janitor(janitor_id, depot_id)

    # ###### GET ALL collector, janitor
    def get_short_information_of_all_collector(self):
        collectors = self.user_repository.get_all_collectors()
        return collectors

    def get_short_information_of_all_janitor(self):
        janitors = self.user_repository.get_all_janitors()
        return janitors

    # ###### GET BY ID - collector id - depot id - get route already assigned
    def get_detail_collector_by_id(self, collector_id):
        collector = self.user_repository.get_collector_by_id(collector_id)
        vehicle = self.user_repository.get_vehicle_of_collector(collector_id)

        if vehicle:
            collector['gg_location'] = vehicle.get('gg_location')
            collector['vehicle_cap'] = vehicle.get('capacity')
        else:
            collector['gg_location'] = ""
            collector['vehicle_cap'] = 0
        return collector

    def get_collector_assigned_route_by_id(self, collector_id):
        return StoredRoute.get_assigned_routes_by_collector_id(collector_id)

    def get_detail_janitor_by_id(self, janitor_id):
        janitor = self.user_repository.get_janitor_by_id(janitor_id)
        return janitor

    def get_collectors_of_depot(self, depot_id):
        return self.user_repository.get_collectors_of_depot(depot_id)

    def get_janitors_of_depot(self, depot_id):
        return self.user_repository.get_janitors_of_depot(depot_id)
