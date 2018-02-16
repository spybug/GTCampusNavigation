import requests
from flask import Flask, request
import xmltodict
import json

app = Flask(__name__)
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"

# All stops are in order
red_stops = [
	(33.7722845,-84.39548),		# Tech Tower
	(33.7727399,-84.3970599),
	(33.7734596,-84.3991581),
	(33.775097,-84.4023891),
	(33.779616,-84.4047091),
	(33.779631,-84.4027473),
	(33.7784499,-84.4008237),
	(33.77819,-84.3974904),
	(33.7770973,-84.3954843),
	(33.776893,-84.3937807),
	(33.7766855,-84.3921335),
	(33.7749537,-84.3920488),
	(33.7736674,-84.3920495),
	(33.7714502,-84.3920986),
	(33.7699398,-84.3916292)	# North Ave
]

@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme. Use /directions endpoint."

# Returns directions from an origin to a destination.
# Mode: The method of travel. 'walking', 'cycling', and 'driving' are straightforward shots to the destination
#	'bus' will walk the user to the nearest bus stop, use GTBus API to route to a second bus stop, and then 
#	walk them to their destination
@app.route('/directions', methods=['GET'])
def get_directions():
	origin = request.args.get('origin')
	destination = request.args.get('destination')
	mode = request.args.get('mode')

	# NOTE: Only red route implemented currently; code will need to be altered to switch routes
	if mode == 'bus':
		origin_stop = (0,0)
		destination_stop = (0,0)
		
		origin_tuple = literal_eval(origin)
		dest_tuple = literal_eval(destination)
		#Locations of origin_stop and destination_stop in list
		oStop_list_loc = 0
		dStop_list_loc = 0
		
		min_distance = 9999
		
		# Find origin_stop
		for counter in range(0, 14):
			if abs(red_stops[counter][0] - origin_tuple[0]) + abs(red_stops[counter][1] - origin_tuple[1]) < min_distance:
				origin_stop = red_stops[counter]
				min_distance = abs(red_stops[counter][0] - origin_tuple[0]) + abs(red_stops[counter][1] - origin_tuple[1])
				oStop_list_loc = counter
		
		min_distance = 9999
		# Find destination_stop
		for counter in range(0, 14):
			if abs(red_stops[counter][0] - destination_tuple[0]) + abs(red_stops[counter][1] - destination_tuple[1]) < min_distance:
				destination_stop = red_stops[counter]
				min_distance = abs(red_stops[counter][0] - destination_tuple[0]) + abs(red_stops[counter][1] - destination_tuple[1])
				dStop_list_loc = counter
		
		# Create waypoints for mapbox route
		bus_stops = [red_route[oStop_list_loc]]
		counter = oStop_list_loc + 1
		while counter != dStop_list_loc and counter != oStop_list_loc:
			counter = counter % 14
			waypoints.append(red_route[counter])
			counter += 1
		bus_stops.append([red_route[oStop_list_loc]])
		
		waypoints = origin + ';' + ";".join("%s,%s" % tup for tup in bus_stops) + ';' + destination
		
		#Get mapbox data
		#NOTE: Fix concatenation of walking into bus ride into walking
		url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{}?overview=full&access_token={}'.format(waypoints, key)
	else:
		if not(origin and destination and mode):  # if not all parameters are supplied
			return 'Missing one or more parameters, need: origin(long,lat), destination(long,lat) and mode(walking, cycling, driving)'

		url = 'https://api.mapbox.com/directions/v5/mapbox/{}/{};{}?overview=full&access_token={}'.format(mode, origin, destination, key)

	response = requests.get(url).content
	return response

# Returns the buses current locations, based on which route you selected
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
        if(vehicle['@routeTag'] == route):
            vehicleIDs.append((vehicle['@id'], vehicle['@heading'], vehicle['@lat'], vehicle['@lon']))

    result = vehicleIDs
    return json.dumps(result)

@app.route('/routes', methods=['GET'])
def get_routes():  # calls gt buses routes method
    route = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/routes'
    headers= {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).content
    xmldict = xmltodict.parse(response)

    return json.dumps(xmldict)

@app.route('/redroutePoly', methods=['GET'])
def get_redroutePoly():

    response = 'yccmEznbbO??M??J?J?~A?ZAh@AL?B?DCLINEHSXSVGJCDILMTSb@Yr@Mb@CLE\\E^AFGr@QlBAF?FADAPKhAq@rHAJAF?DE^Kh@ITIRWb@WZCBSNKFQHA@UFE@SBOB[@]?IAa@AeDK??q@Cg@CI?a@AyAGI??T@zF@xA}A?{@CE?a@AG?_@AC?m@??vA?PAjD?dBEDmAAcBAGU?}B?[?Q?I?e@?c@AwA?S?O@O?{F?OAK?CGMHI|@w@h@g@^]hAcARUHKHKESEQCYAW?A?[@[@YNwA@IHu@BQ@QBM@k@@gE@y@?S?S?O?W?E?u@?K?{@Fk@BMFUBKRi@HK\\g@POPMNIBALG~@i@BCHGJKFSFc@@q@?aB?W@W?g@?O?I?Q?M@iB@k@@oC`@AF?p@EZCxAKJ?j@CL?J?J?V@\\?V?F?R?Z@|@?nA@T?R?N?F?~BApA@jA@`@?^?P?`@@F?`@B@?ZB\\Hf@Dj@@V@vA?h@??_A?OAMACACECGAE@GBGH?JAL?NBPA^wA?WAk@Ag@E]I?lDEbB?x@?H?rDAp@?xB[?{@AgBA'
    return response

if __name__ == '__main__':
  app.run(host='localhost', port=8080, debug=True)
