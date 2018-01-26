import subprocess
import json
import urllib2
from bottle import template, run, post, request, response, get, route

key = 8

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
	data = request.json
	print data
	
	#Parse client JSON into Google URL requests
	origin = data['origin']
	destination = data['destination']
	
	
	#req = urllib2.Request('http://localhost:8080/something')
	#req.add_header('Content-Type', 'application/json')
	#response = urllib2.urlopen(req, json.dumps(data))

"""
@route('/<path>',method = 'POST')
def process(path):
	return subprocess.check_output(['python',path+'.py'],shell=True)
"""
run(host='localhost', port=8080, debug=True)