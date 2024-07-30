from pymongo import MongoClient
import pandas as pd
from flask import url_for
import math


# Load your books data
books_df = pd.read_csv('books_data.csv')



# print(books_df.columns)
# pd.set_option('display.max_columns', None)
# print(books_df)


# Create a mapping dictionary to store unique book_ids for each normalized_title
title_to_book_id = {}

# Assign a unique book_id for each normalized_title
new_book_id = 1  # Starting book_id, can be adjusted as needed
for normalized_title in books_df['Title'].unique():
    title_to_book_id[normalized_title] = new_book_id
    new_book_id += 1
print("after the norm")
# Update the DataFrame with the new consistent book_ids
books_df['Id'] = books_df['Title'].map(title_to_book_id)


books_df['publishedDate'] = books_df['publishedDate'].str.extract(r'(\d{4})')
books_df['publishedDate'] = books_df['publishedDate'].fillna("Unknown")


# Print the updated DataFrame
print("Updated DataFrame with consistent book_id:")
print(books_df)
books_df.to_csv("books_data_new_ids.csv", index=False)


# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['book_recommendation']

# Insert books data into MongoDB
books_collection = db['books_data']
books_collection.insert_many(books_df.to_dict('records'))


# TODO Add the clean data to the process

def clean_book_data(book):
    # Handle None or NaN values and empty lists
    for key, value in book.items():
        if value is None or (isinstance(value, float) and math.isnan(value)):
            if key in ['authors', 'categories', 'description', 'publisher']:
                book[key] = 'Unknown' if key != 'description' else 'No description available'
            elif key == 'image':
                book[key] = url_for('static', filename='default_book_cover.jpg')
            elif key == 'ratingsCount':
                book[key] = 'Not rated'
            elif key == 'publishedDate':
                book[key] = 'Unknown'
        elif isinstance(value, list) and not value:
            book[key] = 'Unknown'
    return book