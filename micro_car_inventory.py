import json
from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import requests
import amqp_connection
from sqlalchemy import event
from os import environ
from sqlalchemy import  Numeric

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/Cars'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cars(db.Model):
    __tablename__ = 'Cars'

    vehicle_id = db.Column(db.Integer, primary_key=True)
    cartype = db.Column(db.String(64), nullable=False)
    brand = db.Column(db.String(64),nullable=False)
    model = db.Column(db.String(64))
    latitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    longitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    availability = db.Column(db.String(8), nullable=False)
    per_hr_price = db.Column(Numeric(precision=10, scale=2), nullable=False)

    def __init__(self, vehicle_id, cartype, brand, model, latitude, longitude, availablity, per_hr_price):
        self.vehicle_id = vehicle_id
        self.carType = cartype
        self.brand = brand
        self.model = model
        self.latitude = latitude
        self.longitude = longitude
        self.availability = availablity
        self.per_hr_price = per_hr_price

    def json(self):
        return {"vehicle_id": self.vehicle_id, "cartype": self.cartype, "brand": self.brand, "model": self.model,"latitude": self.latitude, "longitude": self.longitude, "availability": self.availability, "per_hr_price": self.per_hr_price}

#showing all the cars that are available
@app.route("/cars")
def get_all():
    carList = db.session.scalars(db.select(Cars)).all()

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
            "message": "There are no available cars."
        }
    ), 404

@app.route("/cars/<vehicle_id>", methods=['GET'])
def getCarByCarID(vehicle_id):
    car = db.session.scalars(
    	db.select(Cars).filter_by(vehicle_id=vehicle_id)
        .limit(1)).first()


    if car:
        return jsonify(
            {
                "code": 200,
                "data": car.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Car not found."
        }
    ), 404

#Google distance matrix
def get_distance_matrix(origins, destinations, api_key):
    """Fetch distances from Google Distance Matrix API."""
    distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    payload = {
        'origins': '|'.join(origins),
        'destinations': '|'.join(destinations),
        'key': api_key
    }
    response = requests.get(distance_matrix_url, params=payload)
    return response.json()


#returning cars that are near to me
@app.route("/cars/locationNearMe", methods=["GET"])
def find_by_nearest_distance():
    
    data = request.get_json()

    Latitude = data['lat']
    Longitude = data['long']
    # Expecting 'lat,long
    user_location = f"{Latitude},{Longitude}"
    
    all_cars = Cars.query.filter((Cars.availability == "Booked") | (Cars.availability == "Unbooked")).all()
    if not all_cars:
        return jsonify({"code": 404, "message": "Only damaged cars found"}), 404

    # Prepare to call the Distance Matrix API
    destinations = [f"{car.latitude},{car.longitude}" for car in all_cars]

    distances_response = get_distance_matrix([user_location], destinations, "AIzaSyBpPsrV2pGU20DQwJPqU5sGooE4htyfbEQ")

    elements = distances_response['rows'][0]['elements']

    # Lists to hold your data
    distance_values = []

    # Iterate over each element
    for elem in elements:
            # Check if the status is OK to safely access 'distance' and 'duration'
        if elem['status'] == 'OK':
                # Now we're sure 'distance' exists, we can safely access it
            distance_values.append(elem['distance']['value'])
        else:
                # For elements with ZERO_RESULTS or any status other than OK,
                # append None or a placeholder to indicate the data isn't available
            distance_values.append(None)  # or a large value like float('inf')
    
        # Assign a large value to 'None' entries to ensure they are not selected as the minimum
        distance_values_with_default = [value if value is not None else float('inf') for value in distance_values]

        
        car_distance_pairs = zip(all_cars, distance_values_with_default)

# Step 2: Sort the cars by distance (ascending order), placing 'inf' values at the end
        sorted_pairs = sorted(car_distance_pairs, key=lambda pair: pair[1])

        # To sort in descending order based on distance, you can reverse the list
        # But usually, we want the nearest (smallest distance) first, hence no reverse in this context
        # If you truly need descending order, add reverse=True to the sorted function

        # Step 3: Extract the cars in sorted order for the response
        # sorted_cars = [pair[0] for pair in sorted_pairs]

        # Now, assuming you have a method to serialize a car object, e.g., car.json()
        # Convert each car in the sorted list to its JSON representation
        # sorted_cars_json = [car.json() for car in sorted_cars]

        sorted_cars_json = []
        for pair in sorted_pairs:
            car = pair[0].json()
            car["distance"] = pair[1]
            sorted_cars_json.append(car)

    return jsonify({"code": 200, "CarList": sorted_cars_json})


@app.route("/cars/book", methods=["PUT"])
def book_car():
    data = request.get_json()
    if not data or 'vehicle_id' not in data:
        return jsonify({"code": 400, "error": "Missing vehicle ID"}), 400
    
    requested_vehicle_id = data['vehicle_id']
    
    requested_car = Cars.query.filter_by(vehicle_id = requested_vehicle_id).first()
    if requested_car != None:
        requested_car.availability = "Booked"
        db.session.commit()
        return jsonify({"code": 200, "message": "Car has been booked successfully.", "vehicle_id": requested_vehicle_id}), 200
    
    return jsonify({"code": 404, "message": "No car found with specified vehicle id"}), 404
        
                
# listen to the changes in the sql and update and send to the notif
def after_car_status_change(mapper, connection, target):
    if target.availability == "Unbooked":
        message = {
            'car_id': target.vehicle_id,
            'message': "The car you were waiting for is now available."
        }
        send_message_to_queue(json.dumps(message))
    else:
        message = {
            'car_id': target.vehicle_id,
            'message': "Someone has booked the car"
        }
        send_message_to_queue(json.dumps(message))

# Attach the event listener to the Car model
event.listen(Cars, 'after_update', after_car_status_change)

        
#Wait for car availability, if user wants a particular car
@app.route("/cars/waitForAvailability", methods=["POST"])
def wait_for_availability():
    data = request.get_json()
    car_id = data['vehicle_id']

    reservedCar = db.session.query(Cars).filter_by(
                vehicle_id = car_id
        ).first()
    
    if reservedCar.availability == "Booked":
        # No need to start a background task, the event listener will handle it
        message = "You've been added to the waiting list. We will notify you when the car becomes available."
        return jsonify({"code":201,"message": message})
    else:
        message = "Car is available."
        return jsonify({"code":200,"message": message})
    
    

def send_message_to_queue(message):
    try:
        channel = amqp_connection.create_connection().channel()
        channel.basic_publish(exchange=exchangename, routing_key="car.request", body=json.dumps(message))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
r_queue_name = 'Request_Car'

exchangename = "notifications_exchange"
exchangetype = "topic"

def receiveNotifications(channel):
    
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=r_queue_name, on_message_callback=callback, auto_ack=True)
        print('Notifications: Consuming from queue:', r_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
            #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
        if(r_queue_name == "Request_Car"):
            book_car(r_queue_name)
    
    except pika.exceptions.AMQPError as e:
        print(f"Notifications: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("Notifications: Program interrupted by user.") 

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nNotifications: Received a Notification by " + __file__)
    processNotifications(json.loads(body))
    print()
    
def processNotifications(notifications):
    print("Notifications: Recording notifications:")
    print(notifications)
    
# update car availability status as "damaged"
@app.route("/cars/<vehicle_id>", methods=['PUT'])
def update_availability(vehicle_id):
    try:
        car = db.session.scalars(
        db.select(Cars).filter_by(vehicle_id=vehicle_id).
        limit(1)).first()
        if not car:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "vehicle_id": vehicle_id
                    },
                    "message": "Vehicle not found."
                }
            ), 404

        # update availability
        car.availability = "Damaged"
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": car.json()
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "vehicle_Id": vehicle_id,
                    "availability": "Damaged"
                },
                "message": "An error occurred while updating the vehicle availability. " + str(e)
            }
        ), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True,threaded=True)

#ssl_context=('cert.pem', 'key.pem'),host='0.0.0.0', 

    
