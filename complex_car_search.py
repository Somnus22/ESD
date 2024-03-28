from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app)

car_inventory_URL = environ.get('car_inventory_URL') or "http://localhost:5000/cars"


@app.route("/findNearestCars",methods=['POST'])
def get_all():
    data = request.get_json()
    if data:
        carsList = invoke_http(car_inventory_URL + "/locationNearMe", method="GET", json=data)
        if len(carsList):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "cars": carsList
                    }
                }
            )
    return jsonify(
        {
            "code": 404,
            "message": "There are no available cars."
        }
    ), 404


if __name__ == '__main__':
    app.run(port=5100, debug=True)


