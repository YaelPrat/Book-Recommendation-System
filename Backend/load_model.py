from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
import json

# Initialize Spark session
spark = SparkSession.builder.appName("BookRecommendationApp").getOrCreate()

# Load ALS model
model_path = "als_model"
als_model = ALSModel.load(model_path)

# Load user_id to UserIdIndex mapping
with open('id_to_user_index.json', 'r') as f:
    id_to_user_index = json.load(f)

# Exporting the spark session, als_model, and id_to_user_index
__all__ = ['spark', 'als_model', 'id_to_user_index']
