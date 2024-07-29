"""
# Install MongoDB and start the service
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Install pymongo
pip install pymongo
"""
from pymongo import MongoClient
import pandas as pd

# Load your books data
#TODO load again with the cleaner data (price =0 and not nun)
books_df = pd.read_csv('clean_rating_new_id.csv')

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['book_recommendation']

# Insert books data into MongoDB
books_collection = db['books_rate']
books_collection.insert_many(books_df.to_dict('records'))

# # Example user data
# users = [
#     {"user_id": "user1", "rated_books": [{"book_id": 1, "rating": 5}, {"book_id": 2, "rating": 4}]},
#     {"user_id": "user2", "rated_books": [{"book_id": 3, "rating": 3}, {"book_id": 4, "rating": 5}]},
#
# {
#   "_id": {
#     "$oid": "66a5fb00f14794a4d123939c"
#   },
#   "user_id": "a1n1yemti9dj86",
#   "rated_books": [
#     {
#       "book_id": 47231,
#       "rating": 4,
#       "title": "the best short stories of o henry"
#     },
#     {
#       "book_id": 47243,
#       "rating": 4,
#       "title": "love of a good woman stories"
#     },
#     {
#       "book_id": 5824,
#       "rating": 5,
#       "title": "little women"
#     },
#     {
#       "book_id": 17369,
#       "rating": 4,
#       "title": "cranford"
#     },
#     {
#       "book_id": 47737,
#       "rating": 4,
#       "title": "a passage to india"
#     },
#     {
#       "book_id": 47781,
#       "rating": 4,
#       "title": "the watersplash"
#     },
#     {
#       "book_id": 48205,
#       "rating": 5,
#       "title": "the house sitter"
#     },
#     {
#       "book_id": 48684,
#       "rating": 4,
#       "title": "coningsby or the new generation"
#     },
#     {
#       "book_id": 48826,
#       "rating": 5,
#       "title": "barnaby rudge"
#     },
#     {
#       "book_id": 48826,
#       "rating": 5,
#       "title": "barnaby rudge"
#     },
#     {
#       "book_id": 8279,
#       "rating": 4,
#       "title": "east of eden"
#     },
#     {
#       "book_id": 50061,
#       "rating": 5,
#       "title": "the adventures of huckleberry finn courage literary classics"
#     },
#     {
#       "book_id": 50160,
#       "rating": 5,
#       "title": "the adventures of tom sawyer courage literary classics"
#     },
#     {
#       "book_id": 50502,
#       "rating": 4,
#       "title": "evelina"
#     },
#     {
#       "book_id": 50541,
#       "rating": 4,
#       "title": "the golden one amelia peabody mysteries book 14"
#     },
#     {
#       "book_id": 50546,
#       "rating": 5,
#       "title": "angels in the gloom world war one novels"
#     },
#     {
#       "book_id": 50602,
#       "rating": 4,
#       "title": "act of mercy a celtic mystery"
#     },
#     {
#       "book_id": 7682,
#       "rating": 5,
#       "title": "long spoon lane charlotte and thomas pitt"
#     },
#     {
#       "book_id": 51076,
#       "rating": 4,
#       "title": "a portrait of the artist as a young man"
#     },
#     {
#       "book_id": 51156,
#       "rating": 5,
#       "title": "fiesta the sun also rises"
#     }
#   ]
# }
# ]

# Insert users data into MongoDB
users_collection = db['users']
# users_collection.insert_many(users)
