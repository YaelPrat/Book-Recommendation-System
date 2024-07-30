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
# rating_df = pd.read_csv('clean_rating_new_id.csv')
#
# # Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['book_recommendation']
#
# # Insert books data into MongoDB
rates_collection = db['books_rate']
# books_collection.insert_many(rating_df.to_dict('records'))

rates_collection.create_index('Id')
rates_collection.create_index('Title')
rates_collection.create_index('User_id')

