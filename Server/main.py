from flask import Flask, request, g
import json
import polyline
import requests
import xmltodict

app = Flask(__name__)
key = "***REMOVED***"


@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme. Use /directions endpoint."


@app.route('/directions', methods=['GET'])
def get_directions():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    mode = request.args.get('mode')

    if not (origin and destination and mode):  # if not all parameters are supplied
        return 'Missing one or more parameters, need: origin(long,lat), destination(long,lat) and mode(walking, cycling, driving)'

    url = 'https://api.mapbox.com/directions/v5/mapbox/{}/{};{}?overview=full&access_token={}'.format(mode, origin,
                                                                                                      destination, key)

    response = requests.get(url).content
    return response

@app.route('/buses', methods=['GET'])
def get_buses():  # calls gt buses vehicles method
    route = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/vehicles'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).content
    xmldict = xmltodict.parse(response)

    if not route:
        return json.dumps(xmldict)

    vehicles = xmldict['body']['vehicle']
    vehicleIDs = []

    for vehicle in vehicles:
        if (vehicle['@routeTag'] == route):
            vehicleIDs.append((vehicle['@id'], vehicle['@heading'], vehicle['@lat'], vehicle['@lon']))

    result = vehicleIDs
    return json.dumps(result)


@app.route('/routes', methods=['GET'])
def get_routes():  # calls gt buses routes method
    routeTag = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/routes'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).content
    xmldict = xmltodict.parse(response)

    if not routeTag:
        return json.dumps(xmldict)

    routes = xmldict['body']['route']
    latLonPaths = []

    for route in routes:
        if (route['@tag'] == routeTag):
            # Loop through all paths for route into lat,lon array
            paths = route['path']
            for path in paths:
                latLonPath = []
                for point in path['point']:
                    try:
                        latLonTuple = (round(float(point['@lat']), 6), round(float(point['@lon']), 6))
                        latLonPath.append(latLonTuple)
                    except ValueError:
                        continue
                latLonPaths.append(latLonPath)
            break

    encodedPolyline = []
    for latLonPath in latLonPaths:
        encodedPolyline.append(polyline.encode(latLonPath, 5))

    json_result = {"route": encodedPolyline}

    return json.dumps(json_result)


@app.route('/bikes', methods=['GET'])
def get_bikes():  # Get bike station locations from relay bikes api

    try:
        url = 'https://relaybikeshare.socialbicycles.com/opendata/station_information.json'
        response = requests.get(url).json()
        response = response['data']['stations']  # only use station info
        stations = []

        for station in response:
            stationInfo = {"station_id": station['station_id'], "name": "Station Name", "lat": station['lat'], "lon": station['lon'],
                           "num_bikes_available": 0, "num_bikes_disabled": 0, "num_docks_available": 0,
                           "is_installed": 0, "is_renting": 0, "is_returning": 0}
            stations.append(stationInfo)

        return json.dumps(stations)
    except Exception as e:
        return str(e)


@app.route('/redroutePoly', methods=['GET'])
def get_redroutePoly():
    response = 'yccmEznbbO??M??J?J?~A?ZAh@AL?B?DCLINEHSXSVGJCDILMTSb@Yr@Mb@CLE\\E^AFGr@QlBAF?FADAPKhAq@rHAJAF?DE^Kh@ITIRWb@WZCBSNKFQHA@UFE@SBOB[@]?IAa@AeDK??q@Cg@CI?a@AyAGI??T@zF@xA}A?{@CE?a@AG?_@AC?m@??vA?PAjD?dBEDmAAcBAGU?}B?[?Q?I?e@?c@AwA?S?O@O?{F?OAK?CGMHI|@w@h@g@^]hAcARUHKHKESEQCYAW?A?[@[@YNwA@IHu@BQ@QBM@k@@gE@y@?S?S?O?W?E?u@?K?{@Fk@BMFUBKRi@HK\\g@POPMNIBALG~@i@BCHGJKFSFc@@q@?aB?W@W?g@?O?I?Q?M@iB@k@@oC`@AF?p@EZCxAKJ?j@CL?J?J?V@\\?V?F?R?Z@|@?nA@T?R?N?F?~BApA@jA@`@?^?P?`@@F?`@B@?ZB\\Hf@Dj@@V@vA?h@??_A?OAMACACECGAE@GBGH?JAL?NBPA^wA?WAk@Ag@E]I?lDEbB?x@?H?rDAp@?xB[?{@AgBA'
    return response


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
