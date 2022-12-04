import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))


class UserRepository:

    def __init__(self) -> None:
        self.collectors_path = os.path.join(root_dir, '../data/collectors.JSON')
        self.janitors_path = os.path.join(root_dir, '../data/janitors.JSON')

    @staticmethod
    def resource(file_path):
        with open(file_path) as f:
            resource = json.load(f)
        return resource

    # ###### GET ALL - collector, janitor
    def get_all_collectors(self):
        return UserRepository.resource(self.collectors_path)

    def get_all_janitors(self):
        return UserRepository.resource(self.janitors_path)

    # ###### GET BY ID - collector, janitor
    def get_detail_collector_by_id(self, collector_id):
        collectors = UserRepository.resource(self.collectors_path)
        for collector in collectors:
            if collector_id == collector.get('id'):
                return collector

        return ""

    def get_detail_janitor_by_id(self, collector_id):
        janitors = UserRepository.resource(self.janitors_path)
        for janitor in janitors:
            if collector_id == janitor.get('id'):
                return janitor

        return ""

    # ###### GET BY DEPOT ID
    def get_collectors_of_depot(self, depot_id):
        return [collector for collector in UserRepository.resource(self.collectors_path)
                if collector['depot_id'] == depot_id]