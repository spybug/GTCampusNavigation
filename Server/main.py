import requests
from flask import Flask, request
import xmltodict
import json

app = Flask(__name__)
key = "pk.eyJ1IjoiZ3RjYW1wdXNuYXZpZ2F0aW9ud2ViIiwiYSI6ImNqZGV0amIxZjBpZWMyd21pYm5keWZqdHYifQ.Cm3ZNFq8KFh9UB7NEzHJ2g"

@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme. Use /directions endpoint."

@app.route('/directions', methods=['GET'])
def get_directions():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    mode = request.args.get('mode')

    if not(origin and destination and mode):  # if not all parameters are supplied
        return 'Missing one or more parameters, need: origin(long,lat), destination(long,lat) and mode(walking, cycling, driving)'

    url = 'https://api.mapbox.com/directions/v5/mapbox/{}/{};{}?overview=full&access_token={}'.format(mode, origin, destination, key)

    response = requests.get(url).content
    return response

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
            vehicleIDs.append((vehicle['@lat'], vehicle['@lon']))

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
