from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import Numeric

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/car'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Car(db.Model):
    __tablename__ = 'Cars'

    Vehicle_Id = db.Column(db.String(13), primary_key=True)
    Type = db.Column(db.String(64), nullable=False)
    Brand = db.Column(db.String(64),nullable=False)
    availability = db.Column(db.Integer, nullable=False)
    Price = db.Column(Numeric(10, 2))

    def __init__(self,Vehicle_Id, Type, Brand,Available, Price):
        self.Vehicle_ID = Vehicle_Id
        self.Type = Type
        self.Brand = Brand
        self.availability = Available
        self.Price = Price

    def json(self):
        return {"Vehicle_ID": self.Vehicle_Id, "Type": self.Type, "Brand": self.Brand,"Availability": self.availability, "Price": self.Price}

@app.route("/cars")
def get_all():
    carList = db.session.scalars(db.select(Car)).all()

    if len(carList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Car": [car.json() for car in carList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no car."
        }
    ), 404
   
# @app.route("/car/near")
# def find_by_nearest_distance(distance):
#     book = db.session.scalars(
#         db.select(Book).filter_by(isbn13=isbn13).
#         limit(1)
# ).first()

#     if book:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": book.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "message": "Book not found."
#         }
#     ), 404

@app.route("/cars/available", methods=['GET'])
def availability():
    if request.method == 'GET':
        available_cars = Car.query.filter_by(availability=1).all()
        if available_cars:
            return jsonify({
                "code": 200,
                "data": {"Cars": [car.json() for car in available_cars]},
                "message": "Available cars retrieved successfully."
            }), 200
        else:
            return jsonify({"code": 404, "message": "No available cars."}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


