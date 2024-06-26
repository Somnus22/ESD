from decimal import Decimal
import json
from flask import Flask, request, jsonify,render_template,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pika
import requests
import amqp_connection
from sqlalchemy import event

from sqlalchemy import  Numeric, asc, func

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/Cars'
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
    
    Latitude = request.args.get('lat')  
    Longitude = request.args.get('long')
    # Expecting 'lat,long
    user_location = f"{Latitude},{Longitude}"
    
    all_cars = Cars.query.filter_by(Availability="Unbooked").all()
    if not all_cars:
        return jsonify({"code": 404, "message": "No available cars found"}), 404

    # Prepare to call the Distance Matrix API
    destinations = [f"{car.Latitude},{car.Longitude}" for car in all_cars]
    origins = [f"{Latitude},{Longitude}"]
    api_key = 'AIzaSyBpPsrV2pGU20DQwJPqU5sGooE4htyfbEQ'
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    payload = {
        'origins': '|'.join(origins),
        'destinations': '|'.join(destinations),
        'key': api_key
    }
    response = requests.get(url, params=payload)
    distances_response = get_distance_matrix([user_location], destinations, "AIzaSyBpPsrV2pGU20DQwJPqU5sGooE4htyfbEQ")

    
    
    elements = distances_response['rows'][0]['elements']

    # Lists to hold your data
    distance_values = []
    distance_texts = []

    # Iterate over each element
    for elem in elements:
            # Check if the status is OK to safely access 'distance' and 'duration'
        if elem['status'] == 'OK':
                # Now we're sure 'distance' exists, we can safely access it
            distance_values.append(elem['distance']['value'])
            distance_texts.append(elem['distance']['text'])
        else:
                # For elements with ZERO_RESULTS or any status other than OK,
                # append None or a placeholder to indicate the data isn't available
            distance_values.append(None)  # or a large value like float('inf')
            distance_texts.append("Not Available")
    
        # Assign a large value to 'None' entries to ensure they are not selected as the minimum
        distance_values_with_default = [value if value is not None else float('inf') for value in distance_values]

        # Now find the index of the minimum value in this new list
        closest_car_index = distance_values_with_default.index(min(distance_values_with_default))
        closest_car = all_cars[closest_car_index]
        
        car_distance_pairs = zip(all_cars, distance_values_with_default)

# Step 2: Sort the cars by distance (ascending order), placing 'inf' values at the end
        sorted_pairs = sorted(car_distance_pairs, key=lambda pair: pair[1])

        # To sort in descending order based on distance, you can reverse the list
        # But usually, we want the nearest (smallest distance) first, hence no reverse in this context
        # If you truly need descending order, add reverse=True to the sorted function

        # Step 3: Extract the cars in sorted order for the response
        sorted_cars = [pair[0] for pair in sorted_pairs]

        # Now, assuming you have a method to serialize a car object, e.g., car.json()
        # Convert each car in the sorted list to its JSON representation
        sorted_cars_json = [car.json() for car in sorted_cars]
                

    return jsonify({"code": 200, "CarList": sorted_cars_json})


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


@app.route("/cars/book", methods=["PUT"])
def book_car():
    data = request.get_json()
    if not data or 'lat' not in data or 'long' not in data:
        return jsonify({"code": 400, "error": "Missing latitude or longitude"}), 400
    
    Latitude = data['lat']
    Longitude = data['long']
    car_type = data.get('type', "")  # Allows for an optional car type filter
    
    user_location = f"{Latitude},{Longitude}"
    
    query_filter = Cars.query.filter_by(Availability="Unbooked")
    if car_type:
        query_filter = query_filter.filter_by(CarType=car_type)
    
    all_cars = query_filter.all()
    
    if not all_cars:
        return jsonify({"code": 404, "message": "No available cars found of the requested type"}), 404
    
    destinations = [f"{car.Latitude},{car.Longitude}" for car in all_cars]
    distances_response = get_distance_matrix([user_location], destinations, "AIzaSyBpPsrV2pGU20DQwJPqU5sGooE4htyfbEQ")
    
    if car_type == "":
        elements = distances_response['rows'][0]['elements']

    # Lists to hold your data
        distance_values = []
        distance_texts = []

    # Iterate over each element
        for elem in elements:
            # Check if the status is OK to safely access 'distance' and 'duration'
            if elem['status'] == 'OK':
                # Now we're sure 'distance' exists, we can safely access it
                distance_values.append(elem['distance']['value'])
                distance_texts.append(elem['distance']['text'])
            else:
                # For elements with ZERO_RESULTS or any status other than OK,
                # append None or a placeholder to indicate the data isn't available
                distance_values.append(None)  # or a large value like float('inf')
                distance_texts.append("Not Available")
    
        # Assign a large value to 'None' entries to ensure they are not selected as the minimum
        distance_values_with_default = [value if value is not None else float('inf') for value in distance_values]

        # Now find the index of the minimum value in this new list
        closest_car_index = distance_values_with_default.index(min(distance_values_with_default))

        # Continue as before
        closest_car = all_cars[closest_car_index]
    

        
        closest_car.Availability = "Booked"  # Update availability
        db.session.commit()
        
        return jsonify({"code": 200, "message": "Car booked successfully.", "CarID": closest_car.Vehicle_Id}), 200
    
    return jsonify({"code": 500, "message": "Error fetching distances from Google API"}), 500
        
                
# listen to the changes in the sql and update and send to the notif
def after_car_status_change(mapper, connection, target):
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
    car_id = data.get('Vehicle_Id')
    user_id = data.get('user_id')

    reservedCar = db.session.query(Cars).filter_by(
                Vehicle_Id = car_id
        ).first()
    
    if reservedCar.Availability == "Booked":
        # No need to start a background task, the event listener will handle it
        message = "You've been added to the waiting list. We will notify you when the car becomes available."
    else:
        message = "Car is available."
    return jsonify({"code":200,"message": message}), 200
    
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

@app.route('/get_car_locations')
def get_car_locations():
    # Connect to your database
    cars = db.session.query(Cars).all()
    
    # Replace 'cars' with your actual table name and adjust column names accordingly

    
    # Convert to a list of dicts to jsonify
    locations_dict = [{"latitude": car.Latitude, "longitude": car.Longitude} for car in cars]
    

    
    return jsonify(locations_dict)

@app.route('/carLocations')
def carLocation():
    return render_template('googleMaps.html')

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
    

if __name__ == '__main__':
    app.run(port=5000, debug=True,threaded=True)

#ssl_context=('cert.pem', 'key.pem'),host='0.0.0.0', 

    
