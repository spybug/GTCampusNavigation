from flask import Flask, request, g
import json
import polyline
import requests
import xmltodict
from myDB import myDB

app = Flask(__name__)
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"
routeTags = {'blue': 'blue', 'express': 'tech', 'green': 'green',
'midnight': 'night', 'red': 'red', 'trolley': 'trolley'}

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

# Returns directions from an origin to a destination.
# Mode: The method of travel. 'walking', 'cycling', and 'driving' are straightforward shots to the destination
#	'bus' will walk the user to the nearest bus stop, use GTBus API to route to a second bus stop, and then 
#	walk them to their destination
@app.route('/directions', methods=['GET'])
def get_directions():
	origin = request.args.get('origin')
	destination = request.args.get('destination')
	mode = request.args.get('mode')

	if mode == 'bus':
		origin_stop = (0,0)
		destination_stop = (0,0)
		
		origin_tuple = literal_eval(origin)
		dest_tuple = literal_eval(destination)
		
		min_distance = 9999
		
		# Get stops from database
		bus_stops = g.sql_db.query_dict_return('SELECT DISTINCT Latitude,Longitude, FROM BusStop', None)
		print bus_stops
		
		# Find origin_stop
		for counter in range(0, 14):
			if abs(bus_stops[counter][0] - origin_tuple[0]) + abs(bus_stops[counter][1] - origin_tuple[1]) < min_distance:
				origin_stop = bus_stops[counter]
				min_distance = abs(bus_stops[counter][0] - origin_tuple[0]) + abs(bus_stops[counter][1] - origin_tuple[1])
		
		min_distance = 9999
		# Find destination_stop
		for counter in range(0, 14):
			if abs(bus_stops[counter][0] - destination_tuple[0]) + abs(bus_stops[counter][1] - destination_tuple[1]) < min_distance:
				destination_stop = bus_stops[counter]
				min_distance = abs(bus_stops[counter][0] - destination_tuple[0]) + abs(bus_stops[counter][1] - destination_tuple[1])
		

		#origin_stop_tag = 
		#destination_stop_tag = 
		
		#TODO: Fix route choosing and arrival_time when GT Buses comes back online
		# Get best bus route and when it will be at the destination
		url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/predictions'
		headers= {
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}
		
		response = requests.get(url, headers=headers).content
		xmldict = xmltodict.parse(response)

		# Get route with lowest arrival time
		#route = ''
		arrival_time = 999999
		"""vehicles = xmldict['body']['predictions']
		for vehicle in vehicles:
			if not(vehicle['@dirTitleBecauseNoPredictions']):
				if (vehicle['@stop_tag'] == origin_stop_tag and vehicle['direction']['prediction']['@seconds'] < arrival_time)
					route = vehicle['@stop_tag']
					arrival_time = vehicle['direction']['prediction']['@seconds']"""
		
		#TODO: Replace query_dict_return with something else
		route_geometry = g.sql_db.query_dict_return('SELECT Geometry FROM BusStop WHERE RouteName = ' + route, None)
		
		#Get mapbox data for walking
		url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{};{}?overview=full&access_token={}'.format(origin, origin_stop, key)
		dummy_JSON = requests.get(url).content
		walking_1 = polyline.decode(json.loads(dummy_JSON)["routes"][0]["geometry"])
		
		url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{};{}?overview=full&access_token={}'.format(destination, destination_stop, key)
		walking_2 = polyline.decode(json.loads(requests.get(url).content)["routes"][0]["geometry"])
		
		#Combine into full geometry, then load into JSON
		full_geometry = polyline.encode(walking_1 + route_geometry + walking_2)
		dummy_JSON = json.loads(dummyJSON)
		dummy_JSON["routes"][0]["geometry"] = full_geometry
		dummy_JSON["routes"][0]["duration"] = arrival_time #TODO: May need to manipulate arrival_time's units
		
		return dummy_JSON
		
	else:
		if not(origin and destination and mode):  # if not all parameters are supplied
			return 'Missing one or more parameters, need: origin(long,lat), destination(long,lat) and mode(walking, cycling, driving)'

		url = 'https://api.mapbox.com/directions/v5/mapbox/{}/{};{}?overview=full&access_token={}'.format(mode, origin, destination, key)

	response = requests.get(url).content
	return response

# Get all current bus information (id, location, direction, etc.) for a specific route
# Available routes:
#	red
#	blue
#	green
#	trolley
#	night	- Midnight Rambler
#	tech	- T/S Express
@app.route('/buses', methods=['GET'])
def get_buses():  # calls gt buses vehicles method
	route = request.args.get('route')

	url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/vehicles'
	headers= {
		'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
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
	routeTag = routeTags.get(request.args.get('route'), None)

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
	
@app.route('/bikes', methods=['GET'])
def get_bikes():  # Get bike station status from relay bikes api
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


if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)
