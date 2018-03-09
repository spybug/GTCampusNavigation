from flask import Flask, request, g
import json
import polyline
import requests
import xmltodict
from myDB import myDB

app = Flask(__name__)
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"


@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme. Use /directions endpoint."


def get_db():
    if not hasattr(g, 'sql_db'):
        g.sql_db = myDB()
    return g.sql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sql_db'):
        if error is None:
            g.sql_db.commit()
        g.sql_db.close()

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
            vehicleInfo = {'id': vehicle['@id'], 'dirTag': vehicle['@dirTag'], 'heading': vehicle['@heading'],
                           'lat': vehicle['@lat'], 'lon': vehicle['@lon']}
            vehicleIDs.append(vehicleInfo)

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
def get_bikes():  # Get bike station status from relay bikes api
    try:
        get_db()
        url = 'https://relaybikeshare.socialbicycles.com/opendata/station_status.json'
        response = requests.get(url).json()
        response = response['data']['stations']  # only use station info
        stations = []

        # Get Static Bike station info such as location from database
        results = g.sql_db.query_dict_return('SELECT * FROM BikeStation', None)

        # Combine with station status info from api request
        for station in response:
            id = station['station_id']
            row = results.get(id)
            stationInfo = {"station_id": id, "name": row[1], "lat": row[2], "lon": row[3],
                           "num_bikes_available": station['num_bikes_available'], "num_bikes_disabled": station['num_bikes_disabled'],
                           "num_docks_available": station['num_docks_available'], "is_installed": station['is_installed'],
                           "is_renting": station['is_renting'], "is_returning": station['is_returning']}
            stations.append(stationInfo)

            # Inserts all the bike stations into the database
            #g.sql_db.query_no_return('INSERT INTO BikeStation (StationID, StationName, Latitude, Longitude) VALUES ( ? , ?, ?, ?);',
                                     #(station['station_id'], station['name'], station['lat'], station['lon']))

        return json.dumps(stations)
    except Exception as e:
        return str(e)


@app.route('/redroutePoly', methods=['GET'])
def get_redroutePoly():
    response = 'yccmEznbbO??M??J?J?~A?ZAh@AL?B?DCLINEHSXSVGJCDILMTSb@Yr@Mb@CLE\\E^AFGr@QlBAF?FADAPKhAq@rHAJAF?DE^Kh@ITIRWb@WZCBSNKFQHA@UFE@SBOB[@]?IAa@AeDK??q@Cg@CI?a@AyAGI??T@zF@xA}A?{@CE?a@AG?_@AC?m@??vA?PAjD?dBEDmAAcBAGU?}B?[?Q?I?e@?c@AwA?S?O@O?{F?OAK?CGMHI|@w@h@g@^]hAcARUHKHKESEQCYAW?A?[@[@YNwA@IHu@BQ@QBM@k@@gE@y@?S?S?O?W?E?u@?K?{@Fk@BMFUBKRi@HK\\g@POPMNIBALG~@i@BCHGJKFSFc@@q@?aB?W@W?g@?O?I?Q?M@iB@k@@oC`@AF?p@EZCxAKJ?j@CL?J?J?V@\\?V?F?R?Z@|@?nA@T?R?N?F?~BApA@jA@`@?^?P?`@@F?`@B@?ZB\\Hf@Dj@@V@vA?h@??_A?OAMACACECGAE@GBGH?JAL?NBPA^wA?WAk@Ag@E]I?lDEbB?x@?H?rDAp@?xB[?{@AgBA'
    return response


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
