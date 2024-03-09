#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import amqp_connection
import json
import pika
import os, sys
#from os import environ
app = Flask(__name__)
CORS(app) 
r_queue_name = 'Request_Car'
a_queue_name = 'Available_Car'
exchangename = "notifications_exchange"
exchangetype="topic"

# Instead of hardcoding the values, we can also get them from the environ as shown below
# a_queue_name = environ.get('Activity_Log') #Activity_Log

def receiveNotifications(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('Notifications: Consuming from queue:', a_queue_name)
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

@app.route('/send_notification', methods=['POST'])
def send_notification():
    if request.method == 'POST':
        data = request.json
        # Extract data from the POST request
        car_id = data.get('car_id')
        user_id = data.get('user_id')
        message = data.get('message')

        # Validate input data
        if not all([car_id, user_id, message]):
            return jsonify({"error": "Missing required fields"}), 400

        # Construct the notification message
        notification_data = {
            'car_id': car_id,
            'user_id': user_id,
            'message': message
        }

        try:
            # Publish the notification message to the queue
            channel = amqp_connection.create_connection().channel()
            channel.basic_publish(exchange=exchangename, routing_key="car.request", body=json.dumps(notification_data))
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5100)
    print("Notifications: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("Notifications: Connection established successfully")
    channel = connection.channel()
    receiveNotifications(channel)
