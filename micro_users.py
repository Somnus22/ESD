from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/esd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'users'

    userID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    phoneNumber = db.Column(db.Integer, nullable=False)
    emailAddress = db.Column(db.String(64), nullable=False)

    def json(self):
        return {"userID": self.userID, "name": self.name, "phoneNumber": self.phoneNumber, "emailAddress": self.emailAddress}


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



@app.route("/user/<int:userID>")
def find_by_userID(userID):
    user = db.session.scalars(
    	db.select(Users).filter_by(userID=userID)
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
      db.select(Users).filter_by(emailAddress = email).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "emailAddress": email
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
                    "emailAddress": email
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
    app.run(port=5001, debug=True)


