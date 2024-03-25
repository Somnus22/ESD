from decimal import Decimal
import json
import logging
import threading
import time
from flask import Flask, request, jsonify,render_template,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import amqp_connection
import math
from sqlalchemy import event

from sqlalchemy import Engine, Numeric, asc, func

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/Cars'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cars(db.Model):
    __tablename__ = 'Cars'

    Vehicle_Id = db.Column(db.Integer, primary_key=True)
    CarType = db.Column(db.String(64), nullable=False)
    Brand = db.Column(db.String(64),nullable=False)
    Model = db.Column(db.String(64))
    Latitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    Longitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    Availability = db.Column(db.String(8), nullable=False)
    Per_Hr_Price = db.Column(Numeric(precision=10, scale=2), nullable=False)

    def __init__(self, Vehicle_Id, CarType, Brand,Model, Latitude, Longitude, Availablity, Per_Hr_Price):
        self.Vehicle_Id = Vehicle_Id
        self.CarType = CarType
        self.Brand = Brand
        self.Model = Model
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Availability = Availablity
        self.Per_Hr_Price = Per_Hr_Price

    def json(self):
        return {"Vehicle_Id": self.Vehicle_Id, "CarType": self.CarType, "Brand": self.Brand, "Model": self.Model,"Latitude": self.Latitude, "Longitude": self.Longitude, "Availability": self.Availability, "Per_Hr_Price": self.Per_Hr_Price}

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

#returning the cars that are close to me 
#for car search
@app.route("/cars/locationNearMe", methods = ["GET"])
def find_by_nearest_distance():
    data = request.get_json()
    Latitude = data['lat']
    Longitude = data['long']
    # car_type = data.get('type') 
    
        
    if Latitude is not None and Longitude is not None:
        all_cars = db.session.query(Cars).filter_by(
            Availability = "Unbooked"
        ).all()
        if all_cars:
            all_cars.sort(key=lambda car: haversine(car.Latitude, car.Longitude, Latitude, Longitude))    
            return jsonify({"code": 200, "CarList": [car.json() for car in all_cars]})
        
        return jsonify({"code": 404, "message": "No available cars found"}), 404
    
    return jsonify({"code": 405, "error": "User location error"})
    
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert latitude and longitude from decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius_of_earth = 6371  # Radius of the Earth in kilometers
    distance = radius_of_earth * c

    return distance


#returning cars that are available

@app.route("/cars/available")
def availability():
    if request.method == 'GET':
        available_cars = Cars.query.filter_by(Availability="Unbooked").all()
        if available_cars:
            good_message = "Available cars retrieved successfully."
            
            return jsonify({
                "code": 200,
                "data": {"Cars": [car.json() for car in available_cars]},
                "message": good_message
            }), 200
        else:
            error_message =  "No available cars."
            send_message_to_queue(error_message)
            return jsonify({"code": 404, "message":error_message}), 404


#receive notification that they want to book the car based on distance
#Car rental
@app.route("/cars/book", methods = ["PUT"])
def book_car():
    data = request.get_json()
    Latitude = data['lat']
    Longitude = data['long']
    car_type = data.get('type', "")  # Default to empty string if 'type' not in data

    
    #book whatever cars first     
    if car_type == "":
        if Latitude is not None and Longitude is not None:
            all_cars = db.session.query(Cars).filter_by(
                Availability = "Unbooked"
            ).all()
            if all_cars:
                sorted_cars = sorted(all_cars, key=lambda car: haversine(car.Latitude, car.Longitude, Latitude, Longitude))
                first_car = sorted_cars[0]
                if first_car:
                    all_cars.availability = "Booked"
                    db.session.commit()
                    good_message =  "Car booked successfully."
                    # send_message_to_queue(good_message)
                    return jsonify({"code": 200, "message": good_message, "Longitude": first_car.Longitude, "Latitude": first_car.Latitude}, 200)
                else:
                    bad_message =  "Car not available or does not exist."
                    # send_message_to_queue(bad_message)
                    return jsonify({"code": 404, "message": bad_message}), 404
    else:
    #book cars based on the type 
        if Latitude is not None and Longitude is not None:
            all_cars = db.session.query(Cars).filter_by(
                CarType = data['type']
            ).all()
            if all_cars:
                sorted_cars = sorted(all_cars, key=lambda car: haversine(car.Latitude, car.Longitude, Latitude, Longitude))
                car_id = data.get('car_id')
                matched_car  = None
                for car in sorted_cars:
                    if car.Vehicle_Id == car_id:  # Assuming the car object has an 'id' attribute that holds its ID
                        matched_car = car
                        break
                if matched_car:
                    matched_car.availability = "Booked"
                    db.session.commit()
                    good_message =  "Car booked successfully."
                    send_message_to_queue(good_message)
                    return jsonify({"code": 200, "message":good_message}), 200
                else:
                    bad_message =  "Car not available or does not exist."
                    send_message_to_queue(bad_message)
                    return jsonify({"code": 404, "message": bad_message}), 404
                
                
# listen to the changes in the sql and update and send to the notif
def after_car_status_change(mapper, connection, target):
    print("its working")
    if target.Availability == "Unbooked":
        message = {
            'car_id': target.Vehicle_Id,
            'message': "The car you were waiting for is now available."
        }
        send_message_to_queue(json.dumps(message))

# Attach the event listener to the Car model
event.listen(Cars, 'after_update', after_car_status_change)

        
#Wait for car availability, if user wants a particular car
@app.route("/cars/waitForAvailability", methods=["POST"])
def wait_for_availability():
    data = request.get_json()
    car_id = data['Vehicle_Id']

    # Message you want to send to the queue
    # message = {
    #     'car_id': car_id,
    #     'user_id': user_id,
    #     'message': "A user is waiting for car availability."
    # }
    reservedCar = db.session.query(Cars).filter_by(
                Vehicle_Id = car_id
        ).first()
    
    if reservedCar.Availability == "Booked":
        # No need to start a background task, the event listener will handle it
        message = "You've been added to the waiting list. We will notify you when the car becomes available."
    else:
        message = "Car is available."
    return jsonify({"message": message}), 200
    
#User ends trip then change the booked to unbooked
@app.route("/end_trip/<car_id>", methods=["POST"])
def end_trip(car_id):
    # Here you would update the car's status to 'Unbooked' in your database

    try:
        reservedCar = db.session.query(Cars).filter_by(Vehicle_Id=car_id).first()
        if reservedCar:
            reservedCar.Availability = "Unbooked"
            db.session.commit()
            
            # Now, check if any user is waiting for this car to become available
            # This could be a function that checks a waiting list and notifies the user(s)
            
            return jsonify({"message": "Trip ended and car is now available."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/endtrip')
def endtripweb():
    return render_template('endtrip.html')


def send_message_to_queue(message):
    try:
        channel = amqp_connection.create_connection().channel()
        channel.basic_publish(exchange=exchangename, routing_key="car.request", body=json.dumps(message))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#idk if here needs to send to available car queue   
# def send_message_to_queue2(message):
#     try:
#         channel = amqp_connection.create_connection().channel()
#         channel.basic_publish(exchange=exchangename, routing_key="car.available", body=json.dumps(message))
#         return jsonify({"status": "success"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Instead of hardcoding the values, we can also get them from the environ as shown below
# a_queue_name = environ.get('Activity_Log') #Activity_Log
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
    

if __name__ == '__main__':
    app.run(port=5000, debug=True,threaded=True)

#ssl_context=('cert.pem', 'key.pem'),host='0.0.0.0', 

    
