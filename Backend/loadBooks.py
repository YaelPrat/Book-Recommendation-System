from pymongo import MongoClient
import pandas as pd

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