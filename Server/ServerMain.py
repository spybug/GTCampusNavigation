import subprocess
import json
import urllib
import re
from bottle import template, run, post, request, response, get, route

key = "AIzaSyCnMawlWDbstS9T6cVN5GTcF1GuokHUVcM"

#Takes an origin and destination and gives a route
#Origin and destination are received in the <path>, separated by a question mark
#EX: <serverpath>/directions/origin?destination
@route('/directions/<path>')
def directions(path):
	#Old JSON code, use later
	"""
	#Read received client JSON
	clientJSON = request.json
	print clientJSON
	
	#Parse client JSON into usable parameters
	origin = clientJSON['origin']
	dest = clientJSON['destination']
	"""
	
	#Parse URL into usable parameters
	#Uses "," as delimiter to split variables
	vars = re.split(r"[/,]", path)
	origin = vars[0]
	dest = vars[1]
	
	#Parse parameters into usable route
	routeRequest = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + dest + "&mode=walking" + "&key=" + key
	
	#Request route
	response = urllib.urlopen(routeRequest)
	data = json.loads(response.read())
	return data

"""
@route('/<path>',method = 'POST')
def process(path):
	return subprocess.check_output(['python',path+'.py'],shell=True)
"""
run(host='localhost', port=8080, debug=True)