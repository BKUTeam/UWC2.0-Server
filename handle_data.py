import json
import random

from locals import Locals


def fix_mcps():
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
        json.dump(mcps, f)


def handle_filled_mcps():
    with open('./data/mcps.JSON', "r+") as f:
        mcps = json.load(f)

    exceeded_percent = 0.7
    exceeded_mcp_percent = 0.8
    filled_threshold = Locals.load_config()['mcp_filled_threshold']
    exceeded_mcp_percent_2 = 0.6

    for mcp in mcps:
        ran_num = random.random()
        if ran_num < exceeded_percent:
            ran_mcp = random.random()

            if ran_mcp < exceeded_mcp_percent:
                mcp['filled'] = random.randint(filled_threshold, 100)
            else:
                mcp['filled'] = random.randint(20, filled_threshold)

        else:
            ran_mcp = random.random()
            if ran_mcp > exceeded_mcp_percent_2:
                mcp['filled'] = random.randint(filled_threshold, 100)
            else:
                mcp['filled'] = random.randint(20, filled_threshold)

        with open("./data/mcps.JSON", "w") as f:
            json.dump(mcps, f, indent=2)


if __name__ == "__main__":
    handle_filled_mcps()
