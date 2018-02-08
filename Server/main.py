import requests
from flask import Flask, request
app = Flask(__name__)

key = "AIzaSyCnMawlWDbstS9T6cVN5GTcF1GuokHUVcM"

@app.route('/')
def get_homepage():
    return "Testing- This page is the default home page. Probably change to have a readme. Use /directions endpoint."

@app.route('/directions', methods=['GET'])
def get_directions():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin + "&destination=" + destination + "&mode=walking" + "&key=" + key

    response = requests.get(url).content
    return response

if __name__ == '__main__':
  app.run(host='localhost', port=8080, debug=True)
