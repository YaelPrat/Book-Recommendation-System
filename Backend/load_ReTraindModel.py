from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import json
from pymongo import MongoClient

# Initialize Spark session
spark = SparkSession.builder \
    .appName("BookRecommendationApp") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .getOrCreate()

# Load ALS model
model_path = "retrained_model"
als_model = ALSModel.load(model_path)

# Load user_id to UserIdIndex mapping
with open('id_to_user_index.json', 'r') as f:
    id_to_user_index = json.load(f)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['book_recommendation']
users_collection = db['users']
books_data_collection = db['books_data']


def update_user_recommendations():
    # Generate recommendations for all users
    print("update users rec start")
    user_recs = als_model.recommendForAllUsers(10)
    print("after model rec")

    # Iterate through each user and update their recommendations in the database
    for row in user_recs.collect():
        print("add user to collection",row)

        user_index = row['UserIdIndex']
        recommendations = row['recommendations']
        recommended_books_ids = [rec[0] for rec in recommendations]

        # Fetch book details from MongoDB
        recommended_books_details = list(books_data_collection.find({'Id': {'$in': recommended_books_ids}}))
        for book in recommended_books_details:
            book['_id'] = str(book['_id'])

        # Find the user ID
        user_id = next((uid for uid, idx in id_to_user_index.items() if idx == user_index), None)

        if user_id:
            # Update the user's recommendations in the database
            users_collection.update_one(
                {'user_id': user_id},
                {'$set': {'recommended_books': recommended_books_details}}
            )


# Call the function to update recommendations
update_user_recommendations()
spark.stop()

