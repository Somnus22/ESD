#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/rental_log", methods=['POST'])
def createRentalLog():
    # JSON data validation
    rental_data = None
    if request.is_json:
        rental_data = request.get_json()
        result = processRentalLog(rental_data)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid rental log entry:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "Ensure that rental log entry is in JSON format."}), 400
        
        
@app.route("/rental_log/<int:logID>", methods=['PUT'])
def cancelLogEntry(logID):
    data = request.get_json()
    log_to_be_deleted = data.get("logID")

    if log_to_be_deleted:
        try:
            db.session.delete(log_to_be_deleted)
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": f"Rental log with LogID {logID} has been removed."
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": f"An error occurred removing the rental log: {str(e)}"
                }
            ), 500
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Rental log not found."
            }
        ), 404
        
        
def processRentalLog(rental_data):
    print("Processing a rental log entry:")
    print(rental_data)
    
    if "ERROR" in rental_data['userID']:
        code = 400
        message = 'Failed creation of rental log entry.'
    else:
        code = 201
        message = 'Successful creation of rental log entry.'
    
    print(message+'\n')

    return {
        'code': code,
        'data': {
            'logID': rental_data['logID']
        },
        'message': message
    }

# Execute this program only if it is run as a script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + ": handling rental log entries ...")
    app.run(host='0.0.0.0', port=5000, debug=True)