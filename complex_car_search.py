from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from invokes import invoke_http
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/esd'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

@app.route("/findNearestCars",methods=['POST'])
def get_all():
    data = request.get_json()
    if data:
        carsList = invoke_http("http://localhost:5000/cars/locationNearMe", method="GET", json=data)
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


