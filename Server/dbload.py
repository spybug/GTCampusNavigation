import json
import polyline
import requests
import xmltodict
import numpy

routeTag = raw_input("Input route: ")

url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/routes'
headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}

response = requests.get(url, headers=headers).content
xmldict = xmltodict.parse(response)


routes = xmldict['body']['route']
latLonPaths = []

for route in routes:
	if (route['@tag'] == routeTag):
		# Loop through all paths for route into lat,lon array
		paths = route['path']
		x = 0
		lastLat = 0
		lastLon = 0
		while x < len(paths):
			print x + 1
			if ((lastLat == round(float(paths[x]['point'][0]['@lat']), 6) and lastLon == round(float(paths[x]['point'][0]['@lon']), 6)) or (lastLat == 0 and lastLon == 0)):
				print "\tLastLat: ", lastLat
				print "\tLastLon: ", lastLon
				path = paths[x]
				latLonPath = []
				for point in path['point']:
					print "\t\tPoint", point
					print
					try:
						latLonTuple = (round(float(point['@lat']), 6), round(float(point['@lon']), 6))
						latLonPath.append(latLonTuple)
					except ValueError:
						continue
					x = 0
					lastLat = round(float(point['@lat']), 6)
					lastLon = round(float(point['@lon']), 6)
					print "\t\tLastLat: ", lastLat
					print "\t\tLastLon: ", lastLon
				latLonPaths.extend(latLonPath)
			x += 1
		break

notencodedPolyline = []
for latLonPath in latLonPaths:
	notencodedPolyline.append(latLonPath)

encodedPolyline = polyline.encode(notencodedPolyline, 5)
print encodedPolyline
#return encodedPolyline

