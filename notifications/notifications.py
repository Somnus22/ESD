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
app = Flask(__name__)
CORS(app) 

r_queue_name = 'Request_Car'
a_queue_name = 'Available_Car'
exchangename = "notifications_exchange"
exchangetype="topic"

def send_simple_message():
    try:
        message = f"The car you wanted to book is now available. Hurry up and book now!"
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org/messages",
            auth=("api", "a54c5ed81fe292a752f7cfd3f62c0c79-b02bcf9f-b48c4038"),
            data={"from": "Excited User <mailgun@sandboxcefaa164afc34eba9933f7f63752ee7f.mailgun.org>",
                  "to": ["dominicjovin7@gmail.com"],
                  "subject": "Hello",
                  "text": message})
        
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
        print('Notifications: Consuming from queue:', r_queue_name)
        messages_consumed = 0
        
        while True:
            method_frame, header_frame, body = channel.basic_get(queue=r_queue_name, auto_ack=True)
            if method_frame:
                print("\nNotifications: Received a Notification")
                notification_data = json.loads(body)
                user_id = notification_data.get('user_id')
                # Calling processNotifications with the notification data and user_id
                processNotifications(notification_data, user_id)
                messages_consumed += 1
            else:
                print('Notifications: No more messages in queue:', r_queue_name)
                break
        
        print(f'Notifications: Consumed {messages_consumed} messages from queue:', r_queue_name)

    except pika.exceptions.AMQPError as e:
        print(f"Notifications: Failed to connect: {e}")

    except KeyboardInterrupt:
        print("Notifications: Program interrupted by user.")

def processNotifications(notifications,user_id):
    print("Notifications: Recording notifications:")
    # url = f"http://localhost:5000/order?user_id={user_id}"
    # user_data = invoke_http(url)
    send_simple_message()
    
    print(notifications)

@app.route('/send_notification', methods=['POST'])
def send_notification():
    if request.method == 'POST':
        data = request.json
        car_id = data.get('car_id')
        user_id = data.get('user_id')
        message = data.get('message')

        if not all([car_id, user_id, message]):
            return jsonify({"error": "Missing required fields"}), 400

        notification_data = {
            'car_id': car_id,
            'user_id': user_id,
            'message': message
        }

        try:
            channel = amqp_connection.create_connection().channel()
            channel.basic_publish(exchange=exchangename, routing_key="car.request", body=json.dumps(notification_data))
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def run_flask_app():
    print("This is flask " + os.path.basename(__file__) + " for sending notifications...")
    app.run(host="0.0.0.0", port=5100)

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
