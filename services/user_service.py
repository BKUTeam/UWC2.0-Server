from repositories.user_repository import UserRepository


class UserService:

    def __init__(self,
                 user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_short_all_collector(self,):
        collectors = self.user_repository.get_all_collector()
        return collectors

    def get_collector_info_by_id(self, collector_id):
        collector = self.user_repository.get_collector_by_id(collector_id)
        return collector
