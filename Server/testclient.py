#Use to quickly test JSON on server

import json
import urllib2
import urllib

"""
data = {
        'origin': 'Ferst+Center+For+the+Arts',
		'destination': 'Clough+Undergraduate+Learning+Commons'
}

req = urllib2.Request('http://localhost:8080/something')
req.add_header('Content-Type', 'application/json')

response = urllib2.urlopen(req, json.dumps(data))
"""

url = "http://localhost:8080/directions/Ferst+Center+For+the+Arts,Clough+Undergraduate+Learning+Commons"
response = urllib.urlopen(url)
print response.read()