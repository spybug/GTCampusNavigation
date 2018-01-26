import subprocess
import json
import urllib
from bottle import template, run, post, request, response, get, route

key = "AIzaSyCnMawlWDbstS9T6cVN5GTcF1GuokHUVcM"

"""
@route('/hello')
def hello():
    return "Hello World!"

@route('/')
@route('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)
"""

@route('/something', method='POST')
def something():
	print("Hello World")
	
	#Read received client JSON
	clientJSON = request.json
	print clientJSON
	
	#Parse client JSON into usable parameters
	origin = clientJSON['origin']
	dest = clientJSON['destination']
	
	#Parse parameters into usable route
	routeRequest = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + dest + "&mode=walking" + "&key=" + key
	
	#Request route
	response = urllib.urlopen(routeRequest)
	data = json.loads(response.read())
	print data

"""
@route('/<path>',method = 'POST')
def process(path):
	return subprocess.check_output(['python',path+'.py'],shell=True)
"""
run(host='localhost', port=8080, debug=True)