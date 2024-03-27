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
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/rental_log'

db = SQLAlchemy(app)

class Rental_log(db.Model):
    __tablename__ = 'rental_log'
    Log_Id = db.Column(db.Integer, primary_key=True)
    Log_Entry_Time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    Vehicle_Id = db.Column(db.Integer, nullable=False)
    User_Id = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.String(10), nullable=False)

    def json(self):
        return {"Log_Id": self.Log_Id, "Log_Entry_Time":self.Log_Entry_Time, "Vehicle_Id": self.Vehicle_Id, "User_Id": self.User_Id,"Status":self.Status}

#create rental log    
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
@app.route("/rental_log/<vehicle_id>", methods=['PUT'])
def update_log_entry(vehicle_id):
    try:
        rental_log = db.session.scalars(
        db.select(Rental_log).filter_by(Vehicle_Id=vehicle_id).order_by(desc(Rental_log.Log_Entry_Time))).first()
        if not rental_log:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "Vehicle_id": vehicle_id
                    },
                    "message": "Rental log for Vehicle ID"  + str(vehicle_id) + "was not found."
                }
            ), 404

        # update availability
        rental_log.Status = "Cancelled"
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
                    "Vehicle_Id": vehicle_id,
                    "Status": "Cancelled"
                },
                "message": "An error occurred while updating the rental log. " + str(e)
            }
        ), 500
    
#get rental log    
@app.route("/rental_log/<user_id>", methods=['GET'])
def getRentalLog(user_id):
    # JSON data validation
    log = db.session.scalars(
        db.select(Rental_log).filter_by(User_Id=user_id).order_by(desc(Rental_log.Log_Entry_Time))).first()

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
    app.run(host='0.0.0.0', port=5002, debug=True)