from decimal import Decimal
from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import requests
import math

from sqlalchemy import Numeric, asc, func

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/esd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cars(db.Model):
    __tablename__ = 'Cars'

    Vehicle_Id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(64), nullable=False)
    Brand = db.Column(db.String(64),nullable=False)
    Latitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    Longitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    Availability = db.Column(db.String(8), nullable=False)
    Per_Hr_Price = db.Column(Numeric(precision=10, scale=2), nullable=False)

    def __init__(self, Vehicle_Id, Type, Brand, Latitude, Longitude, Availablity, Per_Hr_Price):
        self.Vehicle_Id = Vehicle_Id
        self.Type = Type
        self.Brand = Brand
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Availability = Availablity
        self.Per_Hr_Price = Per_Hr_Price

    def json(self):
        return {"Vehicle_Id": self.Vehicle_Id, "Type": self.Type, "Brand": self.Brand,"Latitude": self.Latitude, "Longitude": self.Longitude, "Availability": self.Availability, "Per_Hr_Price": self.Per_Hr_Price}

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


@app.route("/cars/locationNearMe", methods = ["GET"])
def find_by_nearest_distance():
    data = request.get_json()
    Latitude = data['lat']
    Longitude = data['long']
    
        
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


@app.route("/cars/available")
def availability():
    if request.method == 'GET':
        available_cars = Cars.query.filter_by(availability=1).all()
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

@app.route("/cars/book", methods = ["PUT"])
def book_car():
    data = request.json
    car_id = data.get('Vehicle_Id')
    # Assuming you have a user identifier or some data to associate with the booking
    # How to know if the car is used by someone 
    user_id = data.get('userID')

    car = Cars.query.filter_by(id=car_id, availability=1).first()
    if car:
        car.availability = 0  # Mark as unavailable
        # Here you can also create a booking record associating the car with the user_id if needed
        db.session.commit()
        return jsonify({"code": 200, "message": "Car booked successfully."}), 200
    else:
        return jsonify({"code": 404, "message": "Car not available or does not exist."}), 404

def send_message_to_queue(message):
    if(message[0] == "Available"):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='Available_Car')  # Create a queue named 'error_queue'
        channel.basic_publish(exchange='', routing_key='Available_Car', body=message)
        print("Sent message to :", message)
        connection.close()
    else:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='error_msg')  # Create a queue named 'error_queue'
        channel.basic_publish(exchange='', routing_key='error_msg', body=message)
        print("Sent message to error_queue:", message)
        connection.close()

# Instead of hardcoding the values, we can also get them from the environ as shown below
# a_queue_name = environ.get('Activity_Log') #Activity_Log
r_queue_name = 'Request_Car'
a_queue_name = 'Available_Car'
exchangename = "notifications_exchange"
exchangetype = "topic"

def receiveNotifications(channel):
    
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=r_queue_name, on_message_callback=callback, auto_ack=True)
        print('Notifications: Consuming from queue:', r_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
            #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
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
    app.run(port=5000, debug=True)

#ssl_context=('cert.pem', 'key.pem'),host='0.0.0.0', 

    