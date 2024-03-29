from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+mysqlconnector://root@localhost:3306/Users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    email_address = db.Column(db.String(64), nullable=False)

    def json(self):
        return {"user_id": self.user_id, "name": self.name, "phone_number": self.phone_number, "email_address": self.email_address}


@app.route("/user")
def get_all():
    userList = db.session.scalars(db.select(Users)).all()

    if len(userList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [user.json() for user in userList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404



@app.route("/user/<int:user_id>")
def find_by_userID(user_id):
    user = db.session.scalars(
    	db.select(Users).filter_by(user_id=user_id)
        .limit(1)).first()


    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404


@app.route("/user", methods=['POST'])
def create_user():
    data = request.get_json()
    email = data["emailAddress"]
    if (db.session.scalars(
      db.select(Users).filter_by(Email_Address = email).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "Email": email
                },
                "message": "User already exists."
            }
        ), 400

    user = Users(**data)
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "Email": email
                },
                "message": "An error occurred creating the user."
            }
        ), 500


    return jsonify(
        {
            "code": 201,
            "data": user.json()
        }
    ), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


