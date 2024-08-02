from flask import request,Flask, jsonify

from pymongo import MongoClient


app = Flask(__name__)


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

    for book in books:
        if '_id' in book:
            book['_id'] = str(book['_id'])

    return jsonify(books)


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
                    "rating": rating,
                    "new_rating": True,  # Flag indicating the rating is new and unprocessed

                }
            }}
        )
        users_collection.update_one(
            {"user_id": user_id},
            {"$pull": {
                "recommended_books": {
                    "Id": book['Id']
                }
            }}
        )
        return jsonify({'message': 'Rating saved successfully'}), 200
    #TODO Add Event so the model will learn
    else:
        return jsonify({'error': 'Book not found'}), 404



#Test the retraned model



if __name__ == '__main__':
    app.run(debug=True, port=5001)
