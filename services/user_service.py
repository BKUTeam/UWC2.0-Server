from repositories.user_repository import UserRepository


class UserService:

    def __init__(self,
                 user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_short_information_of_all_collector(self):
        collectors = self.user_repository.get_all_collectors()
        return collectors

    def get_short_information_of_all_janitor(self):
        janitors = self.user_repository.get_all_janitors()
        return janitors

    def get_detail_collector_by_id(self, collector_id):
        collector = self.user_repository.get_collector_by_id(collector_id)
        vehicle = self.user_repository.get_vehicle_of_collector(collector_id)
        if vehicle != "":
            collector['gg_location'] = vehicle['gg_location']
            collector['vehicle_cap'] = vehicle['capacity']

        return collector

    def get_detail_janitor_by_id(self, janitor_id):
        janitor = self.user_repository.get_janitor_by_id(janitor_id)
        return janitor


