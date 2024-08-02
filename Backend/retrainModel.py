from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import StringIndexer
from pyspark.ml import Pipeline
from pyspark.ml.recommendation import ALS
from pymongo import MongoClient
import pandas as pd
import sys

conf = SparkConf()
conf.set("spark.executor.memory", "4g")
conf.set("spark.driver.memory", "2g")

# Initialize Spark session with the configuration
spark = SparkSession.builder \
    .appName("BookRecommendationApp") \
    .config(conf=conf) \
    .getOrCreate()

def fetch_new_ratings(db):
    ratings_cursor = db.users.aggregate([
        {"$unwind": "$rated_books"},
        {"$match": {"rated_books.new_rating": True}},
        {"$project": {
            "_id": 0,  # Exclude the _id field
            "user_id": 1,
            "book_id": "$rated_books.book_id",
            "rating": "$rated_books.rating",
            "title": "$rated_books.title"
        }}
    ])
    return pd.DataFrame(list(ratings_cursor))

def load_data(df):
    if df.empty:
        print("No new ratings found.")
        sys.exit(0)
    sdf = spark.createDataFrame(df)
    return sdf.withColumn("rating", col("rating").cast("float"))  # Ensure the rating column is of type float

def rename_columns(df):
    return df.withColumnRenamed("Id", "book_id") \
             .withColumnRenamed("Title", "title") \
             .withColumnRenamed("User_id", "user_id") \
             .withColumnRenamed("review/score", "rating")

def index_data(sdf):
    indexer_user = StringIndexer(inputCol="user_id", outputCol="UserIdIndex")
    indexer_book = StringIndexer(inputCol="book_id", outputCol="BookIdIndex")
    pipeline = Pipeline(stages=[indexer_user, indexer_book])
    model = pipeline.fit(sdf)
    indexed_df = model.transform(sdf)
    print("Schema after indexing:")
    indexed_df.printSchema()
    print("Sample data after indexing:")
    indexed_df.show(5)
    return indexed_df

def train_als_model(data):
    als = ALS(maxIter=5, regParam=0.01, userCol="UserIdIndex", itemCol="BookIdIndex", ratingCol="rating", coldStartStrategy="drop")
    return als.fit(data)

def main():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['book_recommendation']

    new_ratings_df = fetch_new_ratings(db)
    new_ratings_sdf = load_data(new_ratings_df)

    print("Schema of new ratings DataFrame:")
    new_ratings_sdf.printSchema()
    print("Sample data from new ratings DataFrame:")
    new_ratings_sdf.show(5)

    existing_data = spark.read.csv('../data/clean_rating_new_id.csv', header=True, inferSchema=True)
    existing_data = rename_columns(existing_data)
    existing_data = existing_data.withColumn("rating", col("rating").cast("float"))

    print("Schema of existing data DataFrame after renaming:")
    existing_data.printSchema()
    print("Sample data from existing data DataFrame after renaming:")
    existing_data.show(50)

    # Ensure columns are ordered the same way in both DataFrames
    columns = ["user_id", "book_id", "rating", "title"]
    existing_data = existing_data.select(columns)
    new_ratings_sdf = new_ratings_sdf.select(columns)

    combined_data = existing_data.union(new_ratings_sdf)
    combined_data.write.csv('combined_data.csv', header=True, mode='overwrite')

    print("Schema of combined data DataFrame:")
    combined_data.printSchema()
    print("Sample data from combined data DataFrame:")
    combined_data.show(5)

    indexed_data = index_data(combined_data)
    als_model = train_als_model(indexed_data)

    # Save the model, update the database, etc.
    als_model.save("retrained_model")
    print("Model training complete and model saved.")

if __name__ == "__main__":
    main()
