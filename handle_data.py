import json


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


def print_uwc_scenario():

    with open('./data/mcp.JSON', "r") as f:
        mcps = json.load(f)

    with open('./data/depots.JSON', "r") as f:
        depots = json.load(f)

    print("--------------------------------------------------------------------")

    for depot in depots:
        print(f"Depot {depot['id']}")
        print(f"\t")
        print(f"\t")
        print(f"\t")
        print(f"\t")
        print(f"\t")

    print("--------------------------------------------------------------------")



if __name__ == "__main__":
    # fix_mcps()
    print("hello")
