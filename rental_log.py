from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:8892/esd' # change to 3306 on my pc
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RentalLog(db.Model):
    __tablename__ = 'rental_log'

    logID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    logEntryTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    logEntryDesc = db.Column(db.String(255), nullable=False)
    
    # TBC: supposed to reference Car Inventory and User Tables
    
    # carID = db.Column(db.Integer, db.ForeignKey('car.carID'))
    # car = relationship("car", back_populates="rental_logs")
    # # params: <child>,<parent>
    # # TBC: backref? (https://stackoverflow.com/questions/51335298/concepts-of-backref-and-back-populate-in-sqlalchemy)
    
    # userID = db.Column(db.Integer, db.ForeignKey('user.userID'))
    # user = relationship("user", back_populates="rental_logs")
    
    carID = db.Column(db.Integer, nullable=False)
    userID = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            "logID": self.logID,
            "logEntryTime": str(self.logEntryTime),
            "logEntryDesc": self.logEntryDesc,
            "carID": self.carID,
            "userID": self.userID,
        }

@app.route("/rental_log", methods=['POST'])
def create_rental_log():
    data = request.get_json()
    
    logID = data.get("logID")
    log_entry_time = data.get("logEntryTime")
    log_entry_desc = data.get("logEntryDesc")
    carID = data.get("carID")
    userID = data.get("userID")

    rental_log = RentalLog(logID=logID, logEntryTime=log_entry_time, logEntryDesc=log_entry_desc, carID=carID, userID=userID)

    try:
        db.session.add(rental_log)
        db.session.commit()
    except Exception as e: # catches all exceptions indiscriminately
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred adding the rental log: {str(e)}"
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": rental_log.json()
        }
    ), 201

@app.route("/rental_logs/<int:logID>", methods=['PUT']) # PUT cuz updating resource
def cancel_rental_log(logID):
    rental_log = RentalLog.query.get(logID)

    if rental_log:
        try:
            db.session.delete(rental_log)
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": f"Rental log with logID {logID} has been cancelled."
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": f"An error occurred cancelling the rental log: {str(e)}"
                }
            ), 500
    else:
        return jsonify(
            {
                "code": 404,
                "message": "Rental log not found."
            }
        ), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
