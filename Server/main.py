from flask import Flask, request, g
import json
import polyline
import requests
import sys
from db import db

app = Flask(__name__)
try:
    app.config.from_pyfile('config.ini')
except Exception as e:
    print("Error: could not import config.ini.\nPlease make sure to create the config.ini file based on the example or download from google drive.")
    sys.exit()
mapbox_key = app.config['MAPBOX_APIKEY']
routeTags = {'blue': 'blue', 'express': 'tech', 'green': 'green',
             'midnight': 'night', 'red': 'red', 'trolley': 'trolley'}


@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme."


def get_db():
    if not hasattr(g, 'sql_db'):
        g.sql_db = db(app.config['DB_SERVER'],
                      app.config['DB_DATABASE'],
                      app.config['DB_USERNAME'],
                      app.config['DB_PASSWORD'])
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
                                                                                                      destination, mapbox_key)
    response = requests.get(url).content
    return response


# Get all current bus information (id, location, direction, etc) for a specific route
@app.route('/buses', methods=['GET'])
def get_buses():  # calls gt buses vehicles method (json version)
    route = routeTags.get(request.args.get('route'), None)

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/vehicles'
    headers = {'User-Agent': 'GT Nav'}

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
    routeTag = routeTags.get(request.args.get('route'), None)

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/routes'
    headers = {'User-Agent': 'GT Nav'}

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
    headers = {'User-Agent': 'GT Nav'}

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
                query = 'IF NOT EXISTS (SELECT * FROM BusStop WHERE StopTag = ? AND RouteTag = ?)' \
                        'BEGIN INSERT INTO BusStop ' \
                        '(Latitude, Longitude, StopTitle, StopTag, RouteTag) VALUES (?, ?, ?, ?, ?) END;'

                g.sql_db.query_no_return(query, (stop['tag'], route['tag'], lat, lon, stop['title'], stop['tag'], route['tag']))

        return 'Successfully added stops'

    except Exception as e:
        print(str(e))
        return ''


# Get bus stops for a specific route from database
@app.route('/stops', methods=['GET'])
def get_busStops():
    routeTag = routeTags.get(request.args.get('route'), None)

    if routeTag is None:
        return ''

    try:
        get_db()
        stopsInfo = []      # Final result object

        # Get static bus stop information from database
        results = g.sql_db.query_many('SELECT * FROM BusStop WHERE RouteTag = ?', routeTag)
        for row in results:  # For every bus stop returned append information
            stopInfo = {'Latitude': row.Latitude, 'Longitude': row.Longitude,
                        'Title': row.StopTitle, 'StopTag': row.StopTag}
            stopsInfo.append(stopInfo)

        return json.dumps(stopsInfo)

    except Exception as e:
        print(str(e))
        return ''


# Get bus stops for a specific route from database
# Use bus stops to get predictions from gt buses
@app.route('/predictions', methods=['GET'])
def get_predictions():
    routeTag = routeTags.get(request.args.get('route'), None)

    if routeTag is None:
        return ''

    url = 'https://gtbuses.herokuapp.com/api/v1/agencies/georgia-tech/multiPredictions?'
    try:
        get_db()
        stopsInfo = []  # Final result object

        # Get static bus stop information from database
        results = g.sql_db.query_many('SELECT * FROM BusStop WHERE RouteTag = ?', routeTag)
        for row in results:  # For every bus stop returned store information into dictionary
            stopTag = row.StopTag
            url += 'stops=' + routeTag + '|' + stopTag + '&'  # Construct url for predictions

        # print(url)
        # Get Predictions for each stop
        headers = {'User-Agent': 'GT Nav'}
        response = requests.get(url, headers=headers).json()
        predictions = response['predictions']

        for stop in predictions:
            direction = stop.get('direction', None)  # Returns None if there are no predictions

            # If no prediction for this stop
            if direction is None:
                predictions = []
                stopInfo = {'StopTag': stop['stopTag'], 'Prediction': predictions}
                stopsInfo.append(stopInfo)
            else:
                predictions = []
                # get all predictions for this stop
                for prediction in direction['prediction']:
                    time = int(prediction['minutes'])
                    # Only include predictions that aren't greater than 30 minutes
                    if time <= 30:
                        predictions.append(time)
                stopInfo = {'StopTag': stop['stopTag'], 'Prediction': predictions}
                stopsInfo.append(stopInfo)

        return json.dumps(stopsInfo)

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
            stationInfo = {
                "station_id": id, 
                "name": row[1], 
                "lat": row[2], "lon": row[3],
                "num_bikes_available": station['num_bikes_available'], 
                "num_bikes_disabled": station['num_bikes_disabled'],
                "num_docks_available": station['num_docks_available'], 
                "is_installed": station['is_installed'],
                "is_renting": station['is_renting'], 
                "is_returning": station['is_returning']
            }
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


@app.route('/faq', methods=['GET'])
def get_faq():
    return app.send_static_file('FAQ.html')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
