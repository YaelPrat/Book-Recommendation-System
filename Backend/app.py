from flask import request,Flask, jsonify
from pymongo import MongoClient
from confluent_kafka import Producer, Consumer, KafkaException
import json
from threading import Thread
import subprocess
import json
from flask_cors import CORS
from bson.json_util import dumps



app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['book_recommendation']
rating_collection = db['books_rate']
users_collection = db['users']
books_data_collection = db['books_data']


# Kafka
RATING_THRESHOLD = 5
rating_count = 0



# Configure the producer
producer = Producer({'bootstrap.servers': 'localhost:29092'})

def delivery_report(err, msg):

    if err is not None:
        print('Producer-Message delivery failed: {}'.format(err))
    else:
        print('Producer-Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

def log_user_action(user_id, action):
    data = {'user_id': user_id, 'action': action}
    producer.produce('user-actions', key=str(user_id), value=json.dumps(data), callback=delivery_report)
    # Wait for all messages in the Producer queue to be delivered
    producer.flush()


# Configure the consumer
consumer = Consumer({
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['user-actions'])


def process_user_actions():
    global rating_count
    while True:
        msg = consumer.poll(1.0)  # Timeout of 1 second
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        # Parse the message
        print('Consumer-Received message: {}'.format(msg.value().decode('utf-8')))
        data = json.loads(msg.value().decode('utf-8'))
        user_id = data['user_id']
        action = data['action']

        # Increment the rating counter when a rating action is logged
        if action == "rated_book":
            rating_count += 1
            print(f"Consumer-Rating count is now {rating_count}")

        # Check if the threshold has been reached
        if rating_count >= RATING_THRESHOLD:
            # Trigger retrainModel.py
            print("Consumer-Threshold reached, retraining model...")
            subprocess.run(["python", "retrainModel.py"])
            print("Consumer-Model retraining complete.")

            # Trigger loadModel.py to load the new recommendations
            print("Consumer-Loading new recommendations...")
            subprocess.run(["python", "loadModel.py"])
            print("Consumer-Recommendations loaded.")

            # Reset the rating count
            rating_count = 0
def run_consumer():
    process_user_actions()
# @app.route('/test-action', methods=['POST'])
# def test_action():
#     user_id = request.json['user_id']
#     action = request.json['action']
#     log_user_action(user_id, action)
#     return jsonify({"status": "action logged"}), 200

# API
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

        # Log the rating action to Kafka
        log_user_action(user_id, "rated_book")

        return jsonify({'message': 'Rating saved successfully'}), 200
    else:
        return jsonify({'error': 'Book not found'}), 404


@app.route('/search', methods=['GET'])
def search_books():
    try:
        query = request.args.get('query', '')
        search_results_cursor = books_data_collection.find({
            "$or": [
                {"Title": {"$regex": query, "$options": "i"}},
                {"authors": {"$regex": query, "$options": "i"}}
            ]
        }).limit(20)

        # Convert cursor to a list and remove duplicates
        search_results = []
        seen_ids = set()

        for book in search_results_cursor:
            book_id = str(book['_id'])
            if book_id not in seen_ids:
                seen_ids.add(book_id)
                search_results.append(book)

        return dumps(search_results)
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


if __name__ == '__main__':
    consumer_thread = Thread(target=run_consumer)
    consumer_thread.start()
    app.run(debug=True, port=5001)
