from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
#test

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/book'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'Book microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of books'
}
swagger = Swagger(app)

class Book(db.Model):
    __tablename__ = 'book'

    isbn13 = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    availability = db.Column(db.Integer)

    def __init__(self, isbn13, title, price, availability):
        self.isbn13 = isbn13
        self.title = title
        self.price = price
        self.availability = availability

    def json(self):
        return {"isbn13": self.isbn13, "title": self.title, "price": self.price, "availability": self.availability}

@app.route("/book")
def get_all():
    """
    Get all books
    ---
    responses:
        200:
            description: Return all books
        404:
            description: No books
    """

    booklist = db.session.scalars(db.select(Book)).all()

    if len(booklist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "books": [book.json() for book in booklist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no books."
        }
    ), 404
   
@app.route("/book/<string:isbn13>")
def find_by_isbn13(isbn13):
    """
    Get a book by its ISBN13
    ---
    parameters:
        -   in: path
            name: isbn13
            required: true
    responses:
        200:
            description: Return the book with the specified ISBN13
        404:
            description: No book with the specified ISBN13 found

    """

    book = db.session.scalars(
        db.select(Book).filter_by(isbn13=isbn13).
        limit(1)
    ).first()

    if book:
        return jsonify(
            {
                "code": 200,
                "data": book.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Book not found."
        }
    ), 404

@app.route("/book/<string:isbn13>", methods=['POST'])
def create_book(isbn13):
    """
    Create a book by its ISBN13
    ---
    parameters:
        -   in: path
            name: isbn13
            required: true
    requestBody:
        description: Book's details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        title: 
                            type: string
                            description: Book's title
                        price: 
                            type: number
                            description: Book's price
                        availability: 
                            type: integer
                            description: Number in stock

    responses:
        201:
            description: Book created
        400:
            description: Book already exists
        500:
            description: Internal server error

    """

    if (db.session.scalars(
        db.select(Book).filter_by(isbn13=isbn13).
        limit(1)
).first()
):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "isbn13": isbn13
                },
                "message": "Book already exists."
            }
        ), 400

    data = request.get_json()
    book = Book(isbn13, **data)

    try:
        db.session.add(book)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "isbn13": isbn13
                },
                "message": "An error occurred creating the book."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": book.json()
        }
    ), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


