import json

from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

from map_processing_system.elements.route import OptimizeRoute
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService
from services.user_service import UserService
from utils import print_scenario

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('collector_id')
parser.add_argument('janitor_id')

user_repository = UserRepository()
map_repository = MapRepository()
google_api_client = DirectionsAPI()
map_processing_system = MapProcessing(map_repository=map_repository)
map_service = MapService(
    map_processing=map_processing_system,
    map_repository=map_repository,
    user_repository=user_repository
)
user_service = UserService(user_repository=user_repository)

print_scenario(map_repo=map_repository, user_repo=user_repository)


# convert to json data
def obj_dict(obj):
    return obj.__dict__


class RouteResource(Resource):

    # get route for collector id
    def get(self):
        try:
            collector_id = int(request.args.get('collector-id'))
            routes = map_service.get_optimize_routes_for_collector(collector_id)
            collector = user_service.get_detail_collector_by_id(collector_id)
            result = json.dumps({"routes": routes}, default=obj_dict)
            return json.loads(result)
        except Exception as e:
            print(e)
            return "INVALID"

    # assign route for collector id
    def post(self):
        try:
            collector_id = int(request.args.get('collector-id'))
            route_id = int(request.args.get('route-id'))
            result = map_service.assign_route_for_collector(route_id, collector_id)
            return result
        except:
            return "INVALID"


# class CollectorRoutes(Resource):
#
#     def get(self):
#         collector_id = int(request.args.get('collector-id'))
#         routes = map_service.get_optimize_routes_for_collector(collector_id)
#         collector = user_service.get_detail_collector_by_id(collector_id)
#         result = json.dumps({"collector": collector, "route": routes}, default=obj_dict)
#         return result
#
#     # assign route for collector id
#     def post(self):
#         collector_id = int(request.args.get('collector-id'))
#         route_id = int(request.args.get('route-id'))
#         action = str(request.args.get('action'))
#         if action == "ASSIGN":
#             result = map_service.assign_route_for_collector(route_id, collector_id)
#             return result
#
#         # null la true a ._. false la false tai trong service hong co return true -> tui que^n return a ban
#         return ""


class Collector(Resource):

    def get(self):
        collectors = user_service.get_short_information_of_all_collector()
        return collectors


class CollectorDetail(Resource):

    def get(self, collector_id=None):
        if collector_id is not None:
            collector = user_service.get_detail_collector_by_id(collector_id)
            return collector
        else:
            return user_service.get_short_information_of_all_collector()


class CollectorRoute(Resource):

    def get(self, collector_id=None):
        if collector_id is not None:
            route = user_service.get_collector_assigned_route_by_id(collector_id)
            return json.loads(json.dumps(route, default=obj_dict))
        else:
            return user_service.get_short_information_of_all_collector()


class Janitor(Resource):

    def get(self):
        janitors = user_service.get_short_information_of_all_collector()
        return janitors

    def post(self):
        try:
            janitor_id = int(request.args.get('janitor-id'))
            facility_id = int(request.args.get('facility-id'))
            action = str(request.args.get('action'))
            if action == "MCP":
                result = user_service.assign_mcp_to_janitor(facility_id, janitor_id)
            elif action == "DEPOT":
                result = user_service.assign_depot_to_janitor(facility_id, janitor_id)
            return result
        except:
            return "INVALID"


class JanitorDetail(Resource):

    def get(self, janitor_id=None):
        if janitor_id is not None:
            janitor = user_service.get_detail_janitor_by_id(janitor_id)
            return janitor
        else:
            return user_service.get_short_information_of_all_janitor()


class Mcp(Resource):

    def get(self):
        mcps = map_service.get_all_mcps()
        return mcps


class McpDetail(Resource):

    def get(self, mcp_id=None):
        if mcp_id is not None:
            mcp = map_service.get_detail_mcp_by_id(mcp_id)
            return mcp
        else:
            return map_service.get_all_mcps()


class Depot(Resource):

    def get(self):
        depots = map_service.get_all_depots()
        return depots


class DepotDetail(Resource):

    def get(self, depot_id=None):
        if depot_id is not None:
            depot = map_service.get_detail_depot_by_id(depot_id)
            return depot
        else:
            return map_service.get_all_depots()


class DepotMCPs(Resource):
    def get(self, depot_id=None):
        if depot_id is not None:
            mcps = map_service.get_mcps_of_depot(depot_id)
            return mcps
        else:
            return map_service.get_all_depots()


class DepotCollectors(Resource):
    def get(self, depot_id=None):
        if depot_id is not None:
            collectors = user_service.get_collectors_of_depot(depot_id)
            return collectors
        else:
            return map_service.get_all_depots()


class DepotJanitors(Resource):
    def get(self, depot_id=None):
        if depot_id is not None:
            janitors = user_service.get_janitors_of_depot(depot_id)
            return janitors
        else:
            return map_service.get_all_depots()


class Factory(Resource):

    def get(self):
        factories = map_service.get_all_factories()
        return factories


# Task assignment api
api.add_resource(RouteResource, '/api/task-assignment/routes')

# Resource api
api.add_resource(Collector, '/api/resources/collectors/')
api.add_resource(CollectorDetail, '/api/resources/collectors/<int:collector_id>')
api.add_resource(CollectorRoute, '/api/resources/collectors/route/<int:collector_id>')

api.add_resource(Janitor, '/api/resources/janitors/')
api.add_resource(JanitorDetail, '/api/resources/janitors/<int:janitor_id>')

api.add_resource(Mcp, '/api/resources/mcps/')
api.add_resource(McpDetail, '/api/resources/mcps/<int:mcp_id>')

api.add_resource(Depot, '/api/resources/depots/')
api.add_resource(DepotDetail, '/api/resources/depots/<int:depot_id>')
api.add_resource(DepotMCPs, '/api/resources/depots/mcps/<int:depot_id>')
api.add_resource(DepotCollectors, '/api/resources/depots/collectors/<int:depot_id>')
api.add_resource(DepotJanitors, '/api/resources/depots/janitors/<int:depot_id>')

api.add_resource(Factory, '/api/resources/factories/')

if __name__ == '__main__':
    app.run(debug=True)
