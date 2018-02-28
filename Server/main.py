import requests
from flask import Flask, request
import xmltodict
import json

app = Flask(__name__)
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"

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
		destination_stop_tag = ''
		
		origin_tuple = literal_eval(origin)
		dest_tuple = literal_eval(destination)
		
		min_distance = 9999
		
		# Get stops from database
		red_stops = [INSERT SQL HERE]
		
		# Find origin_stop
		for counter in range(0, 14):
			if abs(red_stops[counter][0] - origin_tuple[0]) + abs(red_stops[counter][1] - origin_tuple[1]) < min_distance:
				origin_stop = red_stops[counter]
				min_distance = abs(red_stops[counter][0] - origin_tuple[0]) + abs(red_stops[counter][1] - origin_tuple[1])
		
		min_distance = 9999
		# Find destination_stop
		for counter in range(0, 14):
			if abs(red_stops[counter][0] - destination_tuple[0]) + abs(red_stops[counter][1] - destination_tuple[1]) < min_distance:
				destination_stop = red_stops[counter]
				min_distance = abs(red_stops[counter][0] - destination_tuple[0]) + abs(red_stops[counter][1] - destination_tuple[1])
		
		origin_stop_tag = [INSERT SQL HERE]
		destination_stop_tag = [INSERT SQL HERE]
		
		# Get best bus route and when it will be at the destination
		url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/predictions'
		headers= {
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}
		
		response = requests.get(url, headers=headers).content
		xmldict = xmltodict.parse(response)

		route = ''
		lowest_time = 999999
		arrival_time = 0
	
		vehicles = xmldict['body']['predictions']
    
		# For origin stop
		for vehicle in vehicles:
			if (!vehicle['@dirTitleBecauseNoPredictions']):
				#NOTE: Remove routeTag later
				if (vehicle['@stop_tag'] == origin_stop_tag and vehicle['direction']['prediction']['@seconds'] < lowest_time and vehicle['@routeTag'] = 'red')
					route = vehicle['@stop_tag']
					lowest_time = vehicle['direction']['prediction']['@seconds']
		
		# For destination stop
		for vehicle in vehicles:
			if (vehicle['@stop_tag'] == destination_stop_tag and vehicle['@routeTag'] = route)
				route = vehicle['@stop_tag']
				lowest_time = vehicle['direction']['prediction']['@seconds']
				break
		
		#Get mapbox data for walking
		url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{};{}?overview=full&access_token={}'.format(origin, origin_stop, key)
		walking_1 = requests.get(url).content
		
		url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{};{}?overview=full&access_token={}'.format(destination, destination_stop, key)
		walking_2 = requests.get(url).content
		
		
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
        if (vehicle['@routeTag'] == route):
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
