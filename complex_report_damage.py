from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ
import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

report_URL = environ.get("report_URL") or "http://localhost:5003/report"
car_inventory_URL = environ.get("car_inventory_URL") or "http://localhost:5000/cars"
rental_log_URL = environ.get("rental_log_URL") or "http://localhost:5002/rental_log"

#create report
@app.route("/create_report", methods=['POST'])
def create_report():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            report = request.get_json()
            print("\nReceived a report in JSON:", report)
            # Invoke processReportDamage 
            create_report_result = processReportDamage(report)
            return jsonify(create_report_result), create_report_result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "complex_report_damage.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processReportDamage(report):
    #Send the report info
    
    # Invoke the report microservice
    print('\n-----Invoking report microservice-----')
    report_result = invoke_http(report_URL, method='POST', json=report)
    print('report_result:', report_result)
    
    # Update car status as "Damaged" in car inventory
    if report_result["code"] in range (200,300):
        print('\n\n-----Invoking car inventory microservice-----')
        update_result = invoke_http(car_inventory_URL +'/' + str(report['vehicle_id']) , method="PUT")
        print('update_result:', update_result)
        print("\nUpdated car availability to 'Damaged'.\n")
        return report_result
    else:
        return {
            "code": 500,
            "data": {"Report creation": report_result},
            "message": "Report cannot be submitted"
        }

#cancel booking
@app.route("/cancel", methods=['POST'])
def cancel():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            cancel = request.get_json()
            # Invoke update_rental_log
            update_log_result = update_rental_log(cancel)
            return jsonify(update_log_result), update_log_result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "complex_report_damage.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def update_rental_log(report):

    # Invoke the rental log microservice
    print('\n-----Invoking rental log microservice-----')
    rental_log_result = invoke_http(rental_log_URL + "/cancel", method='PUT', json=report)
    print('rental_log_result:', rental_log_result)
    return rental_log_result



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for creating damage reports...")
    app.run(host="0.0.0.0", port=5102, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
