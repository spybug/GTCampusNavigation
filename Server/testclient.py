#Use to quickly test JSON on server

import requests
from flask import Flask, request
import xmltodict
import json
import polyline

"""
data = {
        'origin': 'Ferst+Center+For+the+Arts',
		'destination': 'Clough+Undergraduate+Learning+Commons'
}

req = urllib2.Request('http://localhost:8080/something')
req.add_header('Content-Type', 'application/json')

response = urllib2.urlopen(req, json.dumps(data))
"""
origin = "-122.42,37.78"
origin_stop = "-77.03,38.91"
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"

url = 'https://api.mapbox.com/directions/v5/mapbox/walking/{};{}?overview=full&access_token={}'.format(origin, origin_stop, key)
print json.loads(requests.get(url).content)["routes"][0]["geometry"]