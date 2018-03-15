from flask import Flask, request, g
import json
import polyline
import requests
from db import db

app = Flask(__name__)
key = "***REMOVED***"


@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme."


def get_db():
    if not hasattr(g, 'sql_db'):
        g.sql_db = db()
    return g.sql_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sql_db'):  # If we have a database connection then commit and close
        if error is None:
            g.sql_db.commit()
        g.sql_db.close()

# Get Directions from origin to destination using mode of travel from Mapbox API
@app.route('/directions', methods=['GET'])
def get_directions():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    mode = request.args.get('mode')

    if not (origin and destination and mode):  # if not all parameters are supplied
        return 'Missing one or more parameters, need: origin(long,lat), destination(long,lat) and mode(walking, cycling, driving)'

    # Make request to mapbox
    url = 'https://api.mapbox.com/directions/v5/mapbox/{}/{};{}?overview=full&access_token={}'.format(mode, origin,
                                                                                                      destination, key)
    response = requests.get(url).content
    return response

# Get all current bus information (id, location, direction, etc) for a specific route
@app.route('/buses', methods=['GET'])
def get_buses():  # calls gt buses vehicles method (json version)
    route = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/vehicles'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).json()

    # Return all buses if no route is specified
    if not route:
        return json.dumps(response)

    vehicles = response['vehicle']
    vehicleIDs = []

    for vehicle in vehicles:  # Loop through all the vehicles and only return the ones for the route we want
        if vehicle['routeTag'] == route:
            vehicleInfo = {'id': vehicle['id'], 'dirTag': vehicle['dirTag'], 'heading': vehicle['heading'],
                           'lat': vehicle['lat'], 'lon': vehicle['lon']}
            vehicleIDs.append(vehicleInfo)

    result = vehicleIDs
    return json.dumps(result)

# Get bus route geometry as an encoded polyline for a specific route from gt buses
@app.route('/routes', methods=['GET'])
def get_routes():  # calls gt buses routes method (json version)
    routeTag = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/routes'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).json()

    if not routeTag:  # Return all route information if no route is specified
        return json.dumps(response)

    routes = response['route']
    latLonPath = []
    lastLatLon = None

    for route in routes:
        if route['tag'] == routeTag:  # Find route we want
            # Loop through all paths for route into lat,lon array
            paths = route['path']
            while len(paths) > 0:
                if lastLatLon is None:
                    path = paths.pop(0)  # Get First path and add to list
                    for point in path['point']:
                        try:
                            latLonTuple = (round(float(point['lat']), 6), round(float(point['lon']), 6))
                            latLonPath.append(latLonTuple)
                            lastLatLon = latLonTuple
                        except ValueError:
                            continue

                else:  # For every other path besides the first
                    closetPath = None
                    closetDistance = None
                    for path in paths:  # Find closet path to previous path
                        points = path['point']
                        firstPoint = points[0]  # Check first point in this path to last point
                        try:
                            lat = abs(round(float(firstPoint['lat']), 6))
                            lon = abs(round(float(firstPoint['lon']), 6))
                        except ValueError:
                            continue
                        lastLon, lastLat = lastLatLon
                        distance = abs((lat + lon) - (abs(lastLon) + abs(lastLat)))
                        # Update closet path and distance if we find a closer path
                        if closetDistance is None or distance < closetDistance:
                            closetDistance = distance
                            closetPath = path

                    paths.remove(closetPath)

                    for point in closetPath['point']:  # Add all points from the next closet path
                        try:
                            latLonTuple = (round(float(point['lat']), 6), round(float(point['lon']), 6))
                            latLonPath.append(latLonTuple)
                            lastLatLon = latLonTuple
                        except ValueError:
                            continue

    encodedPolyline = []
    encodedPolyline.append(polyline.encode(latLonPath, 5))

    json_result = {"route": encodedPolyline}

    return json.dumps(json_result)

# Adds all bus stops to the database (given that there aren't in there already)
@app.route('/addBusStops', methods=['GET'])
def add_busStops():  # Calls gt buses route method to get all route information

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/routes'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    try:
        get_db()
        response = requests.get(url, headers=headers).json()

        routes = response['route']

        for route in routes:    # For every route add the bus stops and make association between stop and route
            stops = route['stop']  # Get all stops for this route

            for stop in stops:
                try:
                    # Round bus stop location
                    lat = round(float(stop['lat']), 6)
                    lon = round(float(stop['lon']), 6)
                except ValueError:
                    continue
                # Insert bus stop into the busStops table if it isn't in there already
                # Must match lat/long AND RouteName
                query = 'IF NOT EXISTS (SELECT * FROM BusStop WHERE Latitude = ? AND Longitude = ? AND RouteName = ?)' \
                        'BEGIN INSERT INTO BusStop ' \
                        '(Latitude, Longitude, StopTitle, RouteName) VALUES (?, ?, ?, ?) END;'

                g.sql_db.query_no_return(query, (lat, lon, route['tag'], lat, lon, stop['title'], route['tag']))

        return 'Successfully added stops'

    except Exception as e:
        print(str(e))
        return ''

# Get bus stops for a specific route from database
@app.route('/stops', methods = ['GET'])
def get_busStops():
    routeTag = request.args.get('route')
    if routeTag is None:
        return ''

    try:
        get_db()
        stops = []

        results = g.sql_db.query_many('SELECT * FROM BusStop WHERE RouteName = ?', routeTag)
        for row in results:  # For every bus stop returned, beautify information into json response
            stopInfo = {'Latitude': row[0], 'Longitude': row[1], 'Title': row[2]}
            stops.append(stopInfo)

        return json.dumps(stops)

    except Exception as e:
        print(str(e))
        return ''


# Get all Relay bike station information (location, bikes, docks, etc) from Relay API and our database
@app.route('/bikes', methods=['GET'])
def get_bikes():
    try:
        get_db()
        # Get bike station status from relay bikes api
        url = 'https://relaybikeshare.socialbicycles.com/opendata/station_status.json'
        response = requests.get(url).json()
        response = response['data']['stations']  # only use station info
        stations = []

        # Get Static Bike station info such as location from database
        results = g.sql_db.query_dict_return('SELECT * FROM BikeStation', None)

        # Combine with station status info from api request
        for station in response:
            id = station['station_id']
            row = results.get(id, None)  # Get matching row from database

            # If station doesn't exist in db
            if row is None:
                continue

            # Format all the information we want to return
            stationInfo = {"station_id": id, "name": row[0], "lat": row[1], "lon": row[2],
                           "num_bikes_available": station['num_bikes_available'], "num_bikes_disabled": station['num_bikes_disabled'],
                           "num_docks_available": station['num_docks_available'], "is_installed": station['is_installed'],
                           "is_renting": station['is_renting'], "is_returning": station['is_returning']}
            stations.append(stationInfo)

            # Inserts all the bike stations into the database
            # g.sql_db.query_no_return('INSERT INTO BikeStation (StationID, StationName, Latitude, Longitude) VALUES ( ? , ?, ?, ?);',
                                     #(station['station_id'], station['name'], station['lat'], station['lon']))

            # Statement to Delete Bikes that are out of the area we want to show
            # can also check on insert but this shows bounding box
            # DELETE FROM BikeStation WHERE Latitude < 33.75744 OR Latitude > 33.795217 OR Longitude < -84.418489 OR Longitude > -84.368278;

        return json.dumps(stations)
    except Exception as e:
        print(str(e))
        return ''


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
