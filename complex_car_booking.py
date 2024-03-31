from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from os import environ
import requests
from invokes import invoke_http

import json


app = Flask(__name__)
CORS(app)

user_URL = environ.get('user_URL') or "http://localhost:5001/user"
car_inventory_URL = environ.get('car_inventory_URL') or "http://localhost:5000/cars"
rental_log_URL = environ.get("rental_log_URL") or "http://localhost:5002/rental_log"

@app.route("/car_rental", methods=['POST'])
def car_rental():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            rental_info = request.get_json()
            print("\nReceived a rental request in JSON:", rental_info)

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
            "message": "complex_car_booking.py internal error: " + ex_str
        }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processCarRental(rental_info):

    print('\n-----Invoking Car Inventory microservice-----')
    car_inventory_update = invoke_http(car_inventory_URL + "/book", method="PUT", json = rental_info)
    print('Car Rental Result:', car_inventory_update)
  

    code = car_inventory_update["code"]
    message = json.dumps(car_inventory_update)

    if code == 401:
        print('\n\n-----Publishing the error message with for Car Inventory Microservice-----')
        return {
            "code": 401,
            "data": {"Car Inventory Update": car_inventory_update},
            "message": "Car has already been booked"
        }

    if code not in range(200, 300):
        print('\n\n-----Publishing the error message with for Car Inventory Microservice-----')

       
        
        # 7. Return error
        return {
            "code": 500,
            "data": {"Car Inventory Update": car_inventory_update},
            "message": "Car cannot be booked"
        }

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
    rental_log_info = {**rental_info, **car_inventory_update}    
    rental_log= invoke_http(rental_log_URL,method="POST",json= rental_log_info)
    
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
    print("This is flask " + os.path.basename(__file__) + " for booking a car...")
    app.run(host="0.0.0.0", port=5101, debug=True)