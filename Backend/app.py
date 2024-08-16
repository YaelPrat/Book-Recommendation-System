from flask import request,Flask, jsonify
from pymongo import MongoClient
from confluent_kafka import Producer, Consumer, KafkaException
import json
from threading import Thread


app = Flask(__name__)


# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['book_recommendation']
rating_collection = db['books_rate']
users_collection = db['users']
books_data_collection = db['books_data']


# Kafka

from confluent_kafka import Producer
import json

# Configure the producer
producer = Producer({'bootstrap.servers': 'localhost:29092'})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

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
    while True:
        msg = consumer.poll(1.0)  # Timeout of 1 second
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        # Otherwise, we have a proper message
        print('Received message: {}'.format(msg.value().decode('utf-8')))
        data = json.loads(msg.value().decode('utf-8'))
        # Implement your processing logic here
def run_consumer():
    process_user_actions()
@app.route('/test-action', methods=['POST'])
def test_action():
    user_id = request.json['user_id']
    action = request.json['action']
    log_user_action(user_id, action)
    return jsonify({"status": "action logged"}), 200

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
        return jsonify({'message': 'Rating saved successfully'}), 200
    #TODO Add Event so the model will learn
    else:
        return jsonify({'error': 'Book not found'}), 404



#Test the retraned model



if __name__ == '__main__':
    consumer_thread = Thread(target=run_consumer)
    consumer_thread.start()
    app.run(debug=True, port=5001)
