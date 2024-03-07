#!/usr/bin/env python3
import os
from os import environ
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@host.docker.internal:3306/book'

db = SQLAlchemy(app)

#Create class for Report
class Reports(db.Model):
    __tablename__ = 'reports'

    report_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, nullable=False)
    report_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, report_id, car_id, report_time):
        self.report_id = report_id
        self.car_id = car_id
        self.report_time = report_time

    def json(self):
        return {"report_id": self.report_id, "car_id": self.car_id, "report_time": self.report_time}
    

#Create class for Damages (Contains multiple rows of the same report for different damage notes)
class Damages(db.Model):
    __tablename__ = 'damages'

    report_id = db.Column(db.Integer, db.ForeignKey("reports.report_id") primary_key=True),
    damage_num = db.Column(db.Integer, primary_key=True)
    damage_desc = db.Column(db.String(300), nullable = False)

    def __init__(self, report_id, damage_num, damage_desc):
        self.report_id = report_id
        self.damage_num = damage_num
        self.damage_desc = damage_desc

    def json(self):
        return {"report_id": self.report_id, "damage_num": self.damage_num, "damage_desc": self.damage_desc}



#Create a new report
@app.route("/report", methods=['POST'])
def create_report():


    try:
        db.session.add()
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the report. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": order.json()
        }
    ), 201


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


