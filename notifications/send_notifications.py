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
    app.run(host="0.0.0.0", port=5101)
    
