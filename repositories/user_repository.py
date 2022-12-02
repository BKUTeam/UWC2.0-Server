import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))

class UserRepository:

    def __init__(self) -> None:
        with open(os.path.join(root_dir, '../data/collectors.JSON')) as f:
            self.collectors = json.load(f)

    def get_collector_by_id(self, collector_id):
        for collector in self.collectors:
            if collector['id'] == collector_id:
                return collector
        return None

    def get_all_collector(self):
        return self.collectors
