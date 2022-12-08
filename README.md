# UWC2.0-Server
## Init project
### Install all packages
```
# This command use to install all needed packages
pip install -r requirement.txt
```
### Make use that you have .env file for config
The **.env** file require:
```
GOOGLE_API_KEY=<YOUR GOOGLE API KEY>
MAPBOX_API_KEY=<YOUR MAPBOX API KEY>
API_TYPE=MAPBOX | GOOGLE
MCP_FILLED_THRESHOLD=70
MCP_FILLED_THRESHOLD_LOW=30
DEFAULT_LOADED_PERCENT=70
```
About the api type, we recommend using mapbox, it's easy to register than google api

You don't need to put all api keys, just the api key of type you are using

### To run the server
Go to your command line, make sure you have **python 3.10** (this project are not working with lower version)
```
python api.py
```
## API
You can get the sample api request from Postman

[post_man_uwc_api](https://api.postman.com/collections/24740156-59df8313-e8ab-4d07-ba92-48be93dcce3c?access_key=PMAT-01GKCMC8BRAGDACBVMWPNCZAF7)

### Task assignment API - GET ROUTES
```
localhost:5000/api/task-assignment/routes?collector-id=<CID>&[use-low-threshold]&[use-mcp-pool]
```
**Option:**
- `use-mcp-pool=true` -> use mcp pool to find the routes, default: false


- `use-low-threshold=true` -> use low threshold for filled mcp (30%), default (70%)


- **low-threshold** will not be used when working with **MCP pool**

**Return:**
- `{ routes: [route] } # if success`


- `{ message: "some string" } # if fail`


### Task assignment API - ASSIGN ROUTE
```
localhost:5000/api/task-assignment/routes?collector-id=<CID>&route-id=<RID>&action=ASSIGN
```
**Return:**
- `{ True } # if success`


- `{ False } # if fail`

**Some problem when working with assign API**

When assigning a route for a collector:
- All other routes indicate with the depot (of other collectors) will be released.
- Because the picked mcps might be overlap.


### About the package
We use map direction api to solve UWC problem, make sure you have network connection
