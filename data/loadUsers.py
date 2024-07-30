from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['book_recommendation']  # Replace with your database name
books_collection = db['books_rate']  # Replace with your books collection name
users_collection = db['users']  # Replace with your users collection name
# collection.create_index([('field_name', 1)])

# Define the aggregation pipeline
pipeline = [
    # Step 1: Group by User_id
    {
        '$group': {
            '_id': '$User_id',
            'rated_books': {
                '$push': {
                    'book_id': '$Id',
                    'rating': '$review/score',
                    'title': '$Title'
                }
            }
        }
    },
    # Step 2: Rename fields and format
    {
        '$project': {
            '_id': 0,
            'user_id': '$_id',
            'rated_books': 1
        }
    },
    # Optionally, save the result to a new collection
    {
        '$out': 'users'
    }
]

# Perform the aggregation
results = list(books_collection.aggregate(pipeline))

# Print the results (or process them as needed)
for result in results:
    print(result)

# Optionally, insert the results into the users collection
# users_collection.insert_many(results)

print("Aggregation completed.")
