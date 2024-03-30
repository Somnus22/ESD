#!/usr/bin/env python3


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from os import environ
from datetime import datetime

app = Flask(__name__)
CORS(app)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/Rental_log'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/rental_log'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')

db = SQLAlchemy(app)

class Rental_log(db.Model):
    __tablename__ = 'rental_log'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_entry_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    vehicle_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='CONFIRMED')

    def json(self):
        return {"log_id": self.log_id, "log_entry_time":self.log_entry_time, "vehicle_id": self.vehicle_id, "user_id": self.user_id,"status":self.status}

#create rental log    
#userID/VehicleID/Latitude/Longitude 
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
        

#update rental log as cancelled      
@app.route("/rental_log/cancel", methods=['PUT'])
def update_log_entry():
    report = request.get_json()
    vehicle_id = report['vehicle_id']
    try:
        rental_log = db.session.scalars(
        db.select(Rental_log).filter_by(vehicle_id=vehicle_id).order_by(desc(Rental_log.log_entry_time))).first()
        if not rental_log:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "vehicle_id": vehicle_id
                    },
                    "message": "Rental log for Vehicle ID"  + str(vehicle_id) + "was not found."
                }
            ), 404

        # update availability
        rental_log.status = "Cancelled"
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": rental_log.json()
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "vehicle_id": vehicle_id,
                    "status": "Cancelled"
                },
                "message": "An error occurred while updating the rental log. " + str(e)
            }
        ), 500
    
#get rental log    
@app.route("/rental_log/<user_id>", methods=['GET'])
def getRentalLog(user_id):
    # JSON data validation
    log = db.session.scalars(
        db.select(Rental_log).filter_by(user_id=user_id).order_by(desc(Rental_log.log_entry_time))).first()

    if log:
        return jsonify(
            {
                "code": 200,
                "data": log.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Booking not found."
        }
    ), 404
        
        
def processRentalLog(rental_data):
    print("Processing a rental log entry:")
    print(rental_data)
    new_log = Rental_log(user_id = rental_data["user_id"], vehicle_id = rental_data["vehicle_id"])
    db.session.add(new_log)
    db.session.commit()  # This step generates the log_id

    
    if "ERROR" in rental_data['user_id']:
        code = 400
        message = 'Failed creation of rental log entry.'
    else:
        code = 201
        message = 'Successful creation of rental log entry.'
    
    print(message+'\n')

    return {
        'code': code,
        'data': {
            'log_id': new_log.log_id,
            'log_time': new_log.log_entry_time
        },
        'message': message
    }

# Execute this program only if it is run as a script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + ": handling rental log entries ...")
    app.run(host='0.0.0.0', port=5002, debug=True)