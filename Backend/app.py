from flask import Flask, request, jsonify, redirect, url_for, render_template
import os
import json
from flask import Flask, jsonify, render_template
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
from pymongo import MongoClient

app = Flask(__name__)

# Initialize Spark session
spark = SparkSession.builder.appName("BookRecommendationApp").getOrCreate()

# Load ALS model
model_path = "als_model"
als_model = ALSModel.load(model_path)

# Load user_id to UserIdIndex mapping
with open('id_to_user_index.json', 'r') as f:
    id_to_user_index = json.load(f)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['book_recommendation']
books_collection = db['books_rate']
users_collection = db['users']
books_data_collection = db['books_data']


# book_ids_to_check = [1396, 709, 1035, 1357, 1409, 1370, 1401, 392, 1340, 588]
#
# for book_id in book_ids_to_check:
#     book = books_collection.find_one({'book_id': book_id})
#     print(f"Book ID: {book_id}, Book: {book}")

@app.route('/user/<user_id>/home')
def user_home(user_id):
    # print("inside user-home")
    user = users_collection.find_one({'user_id': user_id})
    if not user:
        return jsonify({"error": f"User with user_id {user_id} not found"}), 404

    print("user", user)
    # Convert ObjectId to string for JSON serialization
    user['_id'] = str(user['_id'])

    # Get user rated books
    user_rated_books = user['rated_books']
    # user_rated_books = user.get('rated_books', [])

    # Find the user index
    user_index = id_to_user_index.get(user_id)
    if user_index is None:
        return jsonify({"error": f"User with user_id {user_id} not found in the model"}), 404

    # Generate recommendations for the user
    try:
        # Print the user index for debugging
        print(f"User index: {user_index}")

        user_recommendations = als_model.recommendForUserSubset(spark.createDataFrame([{'UserIdIndex': user_index}]), 10)

        # Print the raw recommendations for debugging
        print(f"User recommendations: {user_recommendations.collect()}")

        # Extract the recommended book indices
        recommended_books = user_recommendations.collect()[0]['recommendations']
        recommended_books_ids = [rec[0] for rec in recommended_books]  # Extract the first element (book index) from each recommendation

        # Print the recommended book IDs for debugging
        print(f"Recommended book IDs: {recommended_books_ids}")

        # Fetch book details from MongoDB
        recommended_books_details = list(books_data_collection.find({'Id': {'$in': recommended_books_ids}}))
        # Serialize ObjectId and other fields if necessary
        for book in recommended_books_details:
            book['_id'] = str(book['_id'])


        # Print the recommended book details for debugging
        print(f"Recommended book details: {recommended_books_details}")
    except IndexError as e:
        print(f"IndexError: {e}")
        recommended_books_details = []

    return jsonify({
        "rated_books": user_rated_books,
        "recommended_books": recommended_books_details
    })


@app.route('/explore')
def explore_books():
    books = list(books_collection.find().limit(20))
    return jsonify(books)


@app.route('/book/<title>', methods=['GET', 'POST'])
def get_book(title):
    book = books_collection.find_one({"title": title})
    if book:
        if request.method == 'POST':
            rating = request.form.get('rating')
            review = request.form.get('review')
            user_id = request.form.get('user_id')
            # Save rating and review to the database
            users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"rated_books": {"book_id": book['book_id'], "rating": rating, "review": review}}}
            )
            return redirect(url_for('user_home', user_id=user_id))
        return jsonify(book)
    else:
        return jsonify({'error': 'Book not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)
