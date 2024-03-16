#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/report'

db = SQLAlchemy(app)

#Create class for Report
class Report(db.Model):
    __tablename__ = 'report'
    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    car_id = db.Column(db.Integer, nullable=False)
    report_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def json(self):
        return {"report_id": self.report_id, "user_id":self.user_id, "car_id": self.car_id, "report_time": self.report_time}
    

#Create class for Damages (Contains multiple rows of the same report for different damage notes)
class Damage(db.Model):
    __tablename__ = 'damage'
    report_id = db.Column(db.Integer, db.ForeignKey("report.report_id"), primary_key=True)
    damage_num = db.Column(db.Integer, primary_key=True)
    damage_desc = db.Column(db.String(300), nullable=False)

    report = db.relationship(
        'Report', primaryjoin='Report.report_id == Damage.report_id', backref='damage')

    def json(self):
        return {"report_id": self.report_id, "damage_num": self.damage_num, "damage_desc": self.damage_desc}



#Create a new report
@app.route("/report", methods=['POST'])
def create_report():

    user_id = request.json.get('user_id')
    car_id = request.json.get('car_id')
    report = Report(user_id = user_id, car_id = car_id)
    
    damages = request.json.get("damages")
    num = 1

    for x in damages:
        report.damage.append(Damage(
            report_id = report.report_id, damage_num = num, damage_desc = x ))
        num +=1

    try:
        db.session.add(report)
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
            "data": report.json()
        }
    ), 201


if __name__ == '__main__':
    app.run(port=5000, debug=True)


