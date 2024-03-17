from decimal import Decimal
from flask import Flask, request, jsonify,render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
import pika

from requests import Session
from sqlalchemy import Numeric, asc, func

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
    Latitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    Longitude = db.Column(Numeric(precision=10, scale=7))  # Adjust precision and scale as needed
    availability = db.Column(db.Integer, nullable=False)
    Price = db.Column(Numeric(10, 2))

    def __init__(self,Vehicle_Id, Type, Brand, Available, Price,Latitude,Longitude):
        self.Vehicle_ID = Vehicle_Id
        self.Type = Type
        self.Brand = Brand
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.availability = Available
        self.Price = Price

    def json(self):
        return {"Vehicle_ID": self.Vehicle_Id, "Type": self.Type, "Brand": self.Brand,"Latitude": self.Latitude, "Longitude": self.Longitude, "Availability": self.availability, "Price": self.Price}

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
            "message": "There are no car. No available car at the moment"
        }
    ), 404

@app.route("/cars/location")
def render_location_html():
    # Here you can process the latitude and longitude
    # For this example, let's just return them as a JSON response
    
    return render_template("Location.html")


@app.route("/cars/location/nearMe", methods = ["GET","POST"])
def find_by_nearest_distance():
    Latitude = request.args.get('latitude')
    Longitude = request.args.get('longitude')
    # Brand = request.args.get("brand")
    Latitude = float(Latitude)  
    Longitude = float(Longitude)
        
    if Latitude is not None and Longitude is not None:
        nearest_car = Car.query.order_by(
            asc(
                func.sqrt(
                    func.pow(Car.Latitude - Latitude, 2) + func.pow(Car.Longitude - Longitude, 2)
                )
            )
        ).first()

        if nearest_car:
            nearest_car_dict = {
                'Vehicle_Id': nearest_car.Vehicle_Id,
                'Type': nearest_car.Type,
                'Brand': nearest_car.Brand,
                'Latitude': nearest_car.Latitude,
                'Longitude': nearest_car.Longitude,
                'availability': nearest_car.availability,
                'Price': str(nearest_car.Price),  # Convert to string or appropriate format
            }
            return jsonify({"code": 200, "Car": nearest_car_dict})
        else:
            return jsonify({"code": 404, "message": "No available cars found near the specified location with the specified brand."}), 404
    else:
        return jsonify({"error": "Latitude or longitude is missing"})

@app.route("/cars/available", methods=['GET'])
def availability():
    if request.method == 'GET':
        available_cars = Car.query.filter_by(availability=1).all()
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
    app.run(ssl_context=('cert.pem', 'key.pem'),host='0.0.0.0', port=5000, debug=True)


