import json
import requests
import os

from locals import Locals


def gg_location_to_mapbox(gg_location: str):
    new_location = gg_location.split(',')
    new_location.reverse()
    return ','.join(new_location)


class DirectionsAPI:
    GOOGLE_DISTANCE_URL = "https://maps.googleapis.com/maps/api/directions/json" \
                          "?origin={origin}" \
                          "&destination={destination}" \
                          "&mode=driving" \
                          "&departure_time=now" \
                          "&key={api_key}"

    GOOGLE_DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json" \
                                 "?origins={origins}" \
                                 "&destinations={destinations}" \
                                 "&key={api_key}"

    MAPBOX_DISTANCE_MATRIX_URL = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/" \
                                 "{coordinates}?" \
                                 "annotations=distance" \
                                 "&access_token={api_key}"

    @staticmethod
    def get_api_key():
        config = Locals.load_config()
        if config['api_type'] == 'GOOGLE':
            return config['google_api_key']
        elif config['api_type'] == 'MAPBOX':
            return config['mapbox_api_key']
        else:
            raise Exception("API key is invalid")

    @staticmethod
    def get_distance_google_api(origin, destination):
        data = {}
        headers = {}
        response = requests.request(
            method="GET",
            url=DirectionsAPI.GOOGLE_DISTANCE_URL.format(
                origin=origin,
                destination=destination,
                api_key=DirectionsAPI.get_api_key()),
            data=data,
            headers=headers
        )
        return json.loads(response.text)["routes"][0]["legs"][0]["distance"]["value"]

    @staticmethod
    def get_distance_matrix_google_api(origins, destinations):
        # google api only accept request with under 100 single routes
        if len(origins) * len(destinations) <= 100:
            response = requests.request(
                method="GET",
                url=DirectionsAPI.GOOGLE_DISTANCE_MATRIX_URL.format(
                    origins='|'.join([str(ele) for ele in origins]),
                    destinations='|'.join([str(ele) for ele in destinations]),
                    api_key=DirectionsAPI.get_api_key()),
                data={},
                headers={}
            )
            res_json = json.loads(response.text)
            distance_matrix = [
                [ele['distance']['value'] for ele in row['elements']]
                for row in res_json['rows']
            ]
        else:
            slit_index = int(len(destinations) / 2)
            response_1 = requests.request(
                method="GET",
                url=DirectionsAPI.GOOGLE_DISTANCE_MATRIX_URL.format(
                    origins='|'.join([str(ele) for ele in origins]),
                    destinations='|'.join([str(ele) for ele in destinations[0:slit_index]]),
                    api_key=DirectionsAPI.get_api_key()),
            )
            res_json = json.loads(response_1.text)
            distance_matrix = [
                [ele['distance']['value'] for ele in row['elements']]
                for row in res_json['rows']
            ]
            response_2 = requests.request(
                method="GET",
                url=DirectionsAPI.GOOGLE_DISTANCE_MATRIX_URL.format(
                    origins='|'.join([str(ele) for ele in origins]),
                    destinations='|'.join([str(ele) for ele in destinations[slit_index:]]),
                    api_key=DirectionsAPI.get_api_key()),
            )
            res_json = json.loads(response_2.text)
            for idx, row in enumerate(distance_matrix):
                row += [ele['distance']['value'] for ele in res_json['rows'][idx]['elements']]

        return distance_matrix

    @staticmethod
    def get_distance_matrix(list_location, list_id: list[str]) -> list[list[int]]:

        file_path = './distance_matrix/' + (''.join([str(id) for id in list_id])) + '.JSON'
        root_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(root_dir, file_path)
        if os.path.exists(file_path):
            with open(file_path) as distance_f:
                return json.load(distance_f)
        else:
            api_type = DirectionsAPI.get_api_type()
            if api_type == 'GOOGLE':
                matrix_size = len(list_location)
                distance_matrix = []
                for i in range(0, matrix_size):
                    distance_matrix.append([-1] * matrix_size)

                distance_matrix = DirectionsAPI.get_distance_matrix_google_api(list_location, list_location)
            elif api_type == 'MAPBOX':
                distance_matrix = DirectionsAPI.get_distance_matrix_mapbox_api(list_location)
            else:
                raise Exception("API key is invalid")

            with open(file_path, 'w+') as f:
                json.dump(distance_matrix, f, indent=2)

            return distance_matrix

    @staticmethod
    def get_distance_matrix_mapbox_api(list_location):
        res = requests.request(
            'GET',
            url=DirectionsAPI.MAPBOX_DISTANCE_MATRIX_URL.format(
                coordinates=";".join([gg_location_to_mapbox(gg_location) for gg_location in list_location]),
                api_key=DirectionsAPI.get_api_key()
            )
        )
        res_data = json.loads(res.text)
        print(json.dumps(res_data, indent=2))
        return res_data["distances"]
