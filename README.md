# UWC2.0-Server
## Init project
### Install all packages
```
# This command use to install all needed package
pip install -r requirement.txt
```
### Make use that you have .env file for config
The .env require:
```
GOOGLE_API_KEY=<YOUR GOOGLE API KEY>
MAPBOX_API_KEY=<YOUR MAPBOX API KEY>
API_TYPE=MAPBOX | GOOGLE
```
About the api type, we recommend using mapbox, it's easy to register than google api
You don't need to put all api keys, just the api key of type you are using

### To run the server
Go to your command line, make sure you have **python 3.10** (this project are not working with lower version)
```
python api.py
```
### API
You can get the sample api request from Postman
[post_man_uwc_api](https://api.postman.com/collections/24750708-4730c223-1645-4881-815a-bfb0b86c8118?access_key=PMAT-01GKC3QTCG7CVXBBKGSCDJZ37V)

### About the package
We use map direction api to solve UWC problem, make sure you have network connection
