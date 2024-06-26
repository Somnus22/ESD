#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import amqp_connection
import json
import pika
import os, sys
from threading import Thread
import requests
from invokes import invoke_http
from os import environ
from prometheus_flask_exporter import PrometheusMetrics
app = Flask(__name__)
CORS(app) 
metrics = PrometheusMetrics(app)

r_queue_name = 'Request_Car'
exchangename = "notifications_exchange"
exchangetype= "direct"
car_inventory_URL = environ.get("car_inventory_URL") or "http://localhost:5000/cars"
user_URL = environ.get("user_URL") or 'http://localhost:5001/user'

car_dict = {}

def send_simple_message(vehicle_id):
    arr_of_users = car_dict[vehicle_id]
    print(arr_of_users)
    arr_of_emails = []
    for user in arr_of_users:
        print('\n-----Invoking User microservice-----')
        get_user_details = invoke_http(user_URL + "/" + str(user))
        print('User Details:', get_user_details)
    

        # Check the order result; if a failure, send it to the error microservice.
        code = get_user_details["code"]
        message = json.dumps(get_user_details)

        if code not in range(200, 300):

        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
            print('\n\n-----Publishing the error message with for User Microservice-----')
            print({
            "code": 500,
            "data": {"Get User Details": get_user_details},
            "message": "Error in Getting User Details"})
            # return {
            # "code": 500,
            # "data": {"Get User Details": get_user_details},
            # "message": "Error in Getting User Details"}
            

       
        arr_of_emails.append(get_user_details['data']['email_address'])
        # 7. Return error
        
    

    try:
        for email in arr_of_emails:
            print(get_user_details)
            email_message = f"The car with vehicle id: {vehicle_id}, that you wanted to book is now available. Hurry up and book now!"
            response = requests.post(
                "https://api.mailgun.net/v3/sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org/messages",
                auth=("api", "a54c5ed81fe292a752f7cfd3f62c0c79-b02bcf9f-b48c4038"),
                data={"from": "Excited User <mailgun@sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org>",
                    "to": email,
                    "subject": "Hello",
                    "text": email_message})
            
            # Check the response status code
            if response.status_code == 200:
                print("Email sent successfully!")
            else:
                print(f"Failed to send email. Status code: {response.status_code}")
                print(response.text)  # Print error message if available

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def receiveNotifications(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=r_queue_name, on_message_callback=callback, auto_ack=True)
        print('activity_log: Consuming from queue:', r_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"activity_log: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("activity_log: Program interrupted by user.") 

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nactivity_log: Received a Notification by " + __file__)
    processNotifications(json.loads(body))
    print()

def processNotifications(notifications):
    print("Notifications: Recording notifications:")
    print(notifications)
    message_dict = json.loads(notifications)
    car_id = message_dict.get('car_id')
    send_simple_message(car_id)
    
    print(notifications)

@app.route('/send_notification', methods=['POST'])
def send_notification():
    if request.method == 'POST':
        data = request.get_json()
        vehicle_id = data['vehicle_id']
        user_id = data['user_id']

        if not all([vehicle_id, user_id]):
            return {"code":400,"error": "Missing required fields"}

        notification_data = {
            'vehicle_id': vehicle_id,
            'user_id': user_id,
        }

    print('\n-----Invoking Car Inventory microservice-----')
    car_wait_for_availability = invoke_http(car_inventory_URL + "/waitForAvailability",method='POST',json = notification_data)
    print('Car Wait For Availability Result:', car_wait_for_availability)
  

    # Check the order result; if a failure, sen it to the error microservice.
    code = car_wait_for_availability["code"]
    message = json.dumps(car_wait_for_availability)

 
    if code not in range(200, 300):

        print('\n\n-----Publishing the error message with for Car Inventory Microservice-----')

       
        
        # 7. Return error
        return {
            "code": 500,
            "data": {"Wait for Car Availability Update": car_wait_for_availability},
            "message": "User not placed on waiting list"
        }
    
    if vehicle_id in car_dict:
        car_dict[vehicle_id].append(user_id)
    else:
        car_dict[vehicle_id] = [user_id]
    if code == 200:

        return jsonify({
            "code": code,
            "data": {
                "Wait for Car Availability Update": car_wait_for_availability,
            },
            "message": "Car is already available"
        })
    elif code == 201:
        return jsonify({
            "code": code,
            "data": {
                "Wait for Car Availability Update": car_wait_for_availability,
            },
            "message": f"User {user_id} has been placed on waiting list for car {vehicle_id}"
        })


def run_flask_app():
    print("This is flask " + os.path.basename(__file__) + " for sending notifications...")
    app.run(host="0.0.0.0", debug= False, port=5004)

if __name__ == "__main__":
    # Start Flask app in another thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()
    # Start AMQP consumer thread
    channel = amqp_connection.create_connection().channel()
    amqp_thread = Thread(target=receiveNotifications, args=(channel,))
    amqp_thread.start()

    

    # Wait for both threads to finish
    amqp_thread.join()
    flask_thread.join()
