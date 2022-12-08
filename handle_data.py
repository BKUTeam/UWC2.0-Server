import json
import random

from locals import Locals
from repositories.map_repository import MapRepository
from repositories.user_repository import UserRepository
from utils import print_scenario


def reset_data():
    with open('./data/mcps.JSON', "r+") as f:
        mcps = json.load(f)

        depot_id = 0
        for index, mcp in enumerate(mcps):
            if index % 10 == 0:
                depot_id += 1
            if 'depot_id' not in mcp:
                mcp['depot_id'] = depot_id
        for mcp in mcps:
            mcp['state'] = "FREE"
    with open("./data/mcps.JSON", "w") as f:
        json.dump(mcps, f, indent=2)

    with open('./data/collectors.JSON', "r+") as f:
        collectors = json.load(f)

        for col in collectors:
            col.update({'state': 'FREE'})
            col.update({'vehicle_id': random.randint(1, 20)})

    with open("./data/collectors.JSON", "w") as f:
        json.dump(collectors, f, indent=2)


def handle_filled_mcps():
    """
    This method use to set up data with specific scenario

    """

    with open('./data/mcps.JSON', "r+") as f:
        mcps = json.load(f)

    exceeded_percent = 0.8
    exceeded_mcp_percent = 0.9
    filled_threshold = Locals.load_config()['mcp_filled_threshold']
    exceeded_mcp_percent_2 = 0.6

    for mcp in mcps:
        ran_num = random.random()
        if ran_num < exceeded_percent:
            ran_mcp = random.random()

            if ran_mcp < exceeded_mcp_percent:
                mcp['filled'] = random.randint(filled_threshold, 100)
            else:
                mcp['filled'] = random.randint(30, filled_threshold)

        else:
            ran_mcp = random.random()
            if ran_mcp > exceeded_mcp_percent_2:
                mcp['filled'] = random.randint(filled_threshold, 100)
            else:
                mcp['filled'] = random.randint(30, filled_threshold)

        with open("./data/mcps.JSON", "w") as f:
            json.dump(mcps, f, indent=2)


if __name__ == "__main__":
    # reset_data()
    # handle_filled_mcps()
    print_scenario(MapRepository(), UserRepository())
