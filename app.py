import requests
import json
from flask import Flask,  request, jsonify
import os
app = Flask(__name__)
api_key = os.environ['API_KEY']


with app.app_context():
    @app.route("/")
    def meteo():
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (
            lat, lon, api_key)
        response = requests.get(url)
        data = json.loads(response.text)
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': 'La requête à l\'API météo n\'a pas fonctionné. Voici le message renvoyé par l\'API : {}'.format(data)
            }), 500

        return jsonify({
            'status': 'ok',
            'data': data
        })


if __name__ == "__main__":
    app.run(port=8081, debug=True)






