import requests
from flask import Flask, request

app = Flask(__name__)
key = "***REMOVED***"

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
    #print response
    return response

@app.route('/routes', methods=['GET'])
def get_routes():  # calls gt buses routes method
    route = request.args.get('route')

    url = 'https://gtbuses.herokuapp.com/agencies/georgia-tech/routes'
    headers= {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    response = requests.get(url, headers=headers).content
    #print response
    return response

if __name__ == '__main__':
  app.run(host='localhost', port=8080, debug=True)
