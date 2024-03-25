from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import pika
import json


app = Flask(__name__)
CORS(app)

user_URL = "http://localhost:5000/user"
car_inventory_URL = "http://localhost:5000/shipping_record"
rental_log_URL = "http://localhost:5000/rental_log"

@app.route("/car_rental", methods=['POST'])
def car_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_info = request.get_json()
            print("\nReceived a rental request in JSON:", rental_info)


            # do the actual work
            # 1. Send order info {cart items}
            result = processCarRental(rental_info)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processCarRental(rental_info):

    print('\n-----Invoking Car Inventory microservice-----')
    car_inventory_update = invoke_http(car_inventory_URL)
    print('Car Rental Result:', car_inventory_update)
  

    # Check the order result; if a failure, send it to the error microservice.
    code = car_inventory_update["code"]
    message = json.dumps(car_inventory_update)

 
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the error message with for Car Inventory Microservice-----')

       
        
        # 7. Return error
        return {
            "code": 500,
            "data": {"Car Inventory Update": car_inventory_update},
            "message": "Car Cannot Be Booked"
        }

    # Notice that we are publishing to "Activity Log" only when there is no error in order creation.
    # In http version, we first invoked "Activity Log" and then checked for error.
    # Since the "Activity Log" binds to the queue using '#' => any routing_key would be matched 
    # and a message sent to “Error” queue can be received by “Activity Log” too.

    
    
    
    # 5. Send new order to shipping
    # Invoke the shipping record microservice
    print('\n\n-----Invoking users microservice-----')    
    user_id = rental_info.get('user_id')
    user_info= invoke_http(
        user_URL+ f"/{user_id}")
    
    print("User Info:", user_info, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = user_info["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as shipping fails-----')
        print('\n\n-----Publishing the User Info Error-----')

        
        # 7. Return error
        return {
            "code": 400,
            "data": {
                "Car Inventory Update": car_inventory_update,
                "User Info": user_info
            },
            "message": "Error in User Info"
        }


    print('\n\n-----Invoking Rental Log microservice-----')    
    rental_log= invoke_http(rental_log_URL,method="POST",json= rental_info)
    
    print("Rental Log:", rental_log, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = rental_log["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as shipping fails-----')
        print('\n\n-----Publishing the Rental Log Error-----')

        
        # 7. Return error
        return {
            "code": 400,
            "data": {
                "Car Inventory Update": car_inventory_update,
                "User Info": user_info,
                "Rental Log": rental_log
            },
            "message": "Error in Rental Log"
        }

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "Car Inventory Update": car_inventory_update,
                "User Info": user_info,
                "Rental Log": rental_log
        }
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5101, debug=True)