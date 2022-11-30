from multipledispatch import dispatch
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

from map_processing_system.directions_api import DirectionsAPI
from map_processing_system.map_processing import MapProcessing
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from services.map_service import MapService

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


class RouteResource(Resource):

    def get(self):
        collector_id = int(request.args.get('collector-id'))
        result = map_service.get_optimize_routes_for_collector(collector_id)
        return "success"


api.add_resource(RouteResource, '/task-assignment/routes')

if __name__ == '__main__':
    print("url: http://127.0.0.1:5000/task-assignment/routes?collector-id={}")
    app.run(debug=True)
