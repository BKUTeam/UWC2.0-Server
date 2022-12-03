import json

from multipledispatch import dispatch
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

from map_processing_system.elements.route import OptimizeRoute
from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService
from services.user_service import UserService

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('task')

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


# convert to json data
def obj_dict(obj):
    return obj.__dict__


class RouteResource(Resource):

    # get route for collector id
    def get(self):
        collector_id = int(request.args.get('collector-id'))
        routes = map_service.get_optimize_routes_for_collector(collector_id)
        collector = user_service.get_collector_info_by_id(collector_id)
        result = json.dumps({"collector": collector, "route": routes}, default=obj_dict)
        return result

    # assign route for collector id
    def post(self):
        collector_id = int(request.args.get('collector-id'))
        route_id = int(request.args.get('route-id'))
        result = map_service.assign_route_for_collector(route_id, collector_id)
        # null la true a ._. false la false tai trong service hong co return true
        return result


class CollectorResource(Resource):

    # get collector list
    def get(self):
        collectors = user_service.get_short_all_collector()
        return collectors


api.add_resource(RouteResource, '/task-assignment/routes')
api.add_resource(CollectorResource, '/task-assignment/')



if __name__ == '__main__':
    print("get route: http://127.0.0.1:5000/task-assignment/routes?collector-id={}")
    print("post route: http://127.0.0.1:5000/task-assignment/routes?collector-id={}&route-id={}")
    app.run(debug=True)
