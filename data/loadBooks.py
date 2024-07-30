from pymongo import MongoClient
import pandas as pd
import math

# Load your books data
books_df = pd.read_csv('books_data.csv')

# Debug: Print initial data
print("Initial DataFrame:")
print(books_df.head())

# Create a mapping dictionary to store unique book_ids for each normalized_title
title_to_book_id = {}

# Assign a unique book_id for each normalized_title
new_book_id = 1  # Starting book_id, can be adjusted as needed
for normalized_title in books_df['Title'].unique():
    title_to_book_id[normalized_title] = new_book_id
    new_book_id += 1

# Debug: Print title to book ID mapping
print("Title to Book ID Mapping:")
print(title_to_book_id)

# Update the DataFrame with the new consistent book_ids
books_df['Id'] = books_df['Title'].map(title_to_book_id)

# Debug: Print DataFrame after adding IDs
print("DataFrame after adding Ids:")
print(books_df.head())

books_df['publishedDate'] = books_df['publishedDate'].str.extract(r'(\d{4})')
books_df['publishedDate'] = books_df['publishedDate'].fillna("Unknown")

# Debug: Print DataFrame after extracting publishedDate
print("DataFrame after extracting and filling publishedDate:")
print(books_df.head())

# Clean book data
def clean_book_data(book):
    for key, value in book.items():
        if value is None or (isinstance(value, float) and math.isnan(value)):
            if key in ['authors', 'categories', 'description', 'publisher']:
                book[key] = 'Unknown' if key != 'description' else 'No description available'
            elif key == 'image':
                book[key] = '/static/default_book_cover.jpg'  # Set a default URL for the book cover image
            elif key == 'ratingsCount':
                book[key] = 'Not rated'
            elif key == 'publishedDate':
                book[key] = 'Unknown'
        elif isinstance(value, list) and not value:
            book[key] = 'Unknown'
    return book

# Apply cleaning to the DataFrame
books_df = books_df.apply(lambda row: clean_book_data(row.to_dict()), axis=1)

# Convert the Series of dictionaries back to a DataFrame
books_df = pd.DataFrame(books_df.tolist())

# Debug: Print cleaned DataFrame
print("Cleaned DataFrame:")
print(books_df.head())

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['book_recommendation']

# Drop the existing collection if it exists
books_collection = db['books_data']
books_collection.drop()

# Debug: Print confirmation of collection drop
print("Dropped existing books_data collection.")

# Insert cleaned books data into MongoDB
books_collection.insert_many(books_df.to_dict(orient='records'))

# Debug: Print confirmation of data insertion
print("Inserted cleaned data into MongoDB.")

# Create indices to optimize queries
books_collection.create_index('Id')
books_collection.create_index('Title')
books_collection.create_index('authors')
books_collection.create_index('categories')

# Debug: Print confirmation of index creation
print("Created indices on Id, Title, authors, and categories.")
print("Books data cleaned, inserted, and indexed in MongoDB.")
