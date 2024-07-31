from flask import Flask, request, jsonify, redirect, url_for, render_template
import json
from flask import Flask, jsonify, render_template
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
from pymongo import MongoClient
import math
from bson import ObjectId

# from load_model import spark, als_model, id_to_user_index, update_user_recommendations  # Importing Spark and ALS model


app = Flask(__name__)


# # Load user_id to UserIdIndex mapping
# with open('id_to_user_index.json', 'r') as f:
#     id_to_user_index = json.load(f)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['book_recommendation']
rating_collection = db['books_rate']
users_collection = db['users']
books_data_collection = db['books_data']



@app.route('/user/<user_id>/home')
def user_home(user_id):
    user = users_collection.find_one({'user_id': user_id})
    if not user:
        return jsonify({"error": f"User with user_id {user_id} not found"}), 404

    user['_id'] = str(user['_id'])
    user_rated_books = user.get('rated_books', [])
    recommended_books_details = user.get('recommended_books', [])

    return jsonify({
        "rated_books": user_rated_books,
        "recommended_books": recommended_books_details
    })


@app.route('/explore')
def explore_books():
    books = list(books_data_collection.find().limit(20))
    # books = [clean_book_data(book) for book in books]
    # Convert ObjectId to string
    for book in books:
        if '_id' in book:
            book['_id'] = str(book['_id'])

    return jsonify(books)


def clean_book_data(book):
    for key, value in book.items():
        if isinstance(value, float) and math.isnan(value):
            book[key] = None
        elif value == 'nan':
            book[key] = None
    return book


@app.route('/book/<title>', methods=['GET'])
def get_book(title):
    book = books_data_collection.find_one({"Title": title})
    if book:
        book['_id'] = str(book['_id'])  # Convert ObjectId to string
        return jsonify(book)
    else:
        return jsonify({'error': 'Book not found'}), 404

@app.route('/user/<user_id>/rate', methods=['POST'])
def rate_book(user_id):
    data = request.get_json()
    title = data['title']
    rating = data['rating']
    book = books_data_collection.find_one({"Title": title})

    if book:
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {
                "rated_books": {
                    "book_id": book['Id'],
                    "title": book['Title'],
                    "rating": rating
                }
            }}
        )
        return jsonify({'message': 'Rating saved successfully'}), 200
    else:
        return jsonify({'error': 'Book not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
