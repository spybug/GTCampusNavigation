import requests
from flask import Flask, request
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
    url = "https://api.mapbox.com/directions/v5/mapbox/" + mode + "/" + origin + ";" + destination + "?overview=full&access_token=" + key

    response = requests.get(url).content
    return response

if __name__ == '__main__':
  app.run(host='localhost', port=8080, debug=True)
