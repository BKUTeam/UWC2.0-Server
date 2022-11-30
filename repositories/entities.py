class Mcp:

    def __init__(self, id, depot_id, gg_location, capacity, filled, state):
        self.id = id
        self.depot_id = depot_id
        self.gg_location = gg_location
        self.capacity = capacity
        self.filled = filled
        self.state = state


class Depot:
    def __init__(self, id, gg_location):
        self.id = id
        self.gg_location = gg_location


class Factory:
    def __init__(self, id, gg_location):
        self.id = id
        self.gg_location = gg_location


class Vehicle:
    def __int__(self, id, depot_id, gg_location, capacity, state, collector_id):
        self.id = id
        self.depot_id = depot_id
        self.gg_location = gg_location
        self.capacity = capacity
        self.state = state
        self.collector_id = collector_id


class Collector:
    def __init__(self, id, vehicle_id, depot_id):
        self.id = id
        self.vehicle_id = vehicle_id
        self.depot_id = depot_id
