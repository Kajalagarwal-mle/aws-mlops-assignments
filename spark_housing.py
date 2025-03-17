import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Get AWS Glue job name from arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Initialize Spark and Glue contexts
spark = SparkSession.builder.appName(args['JOB_NAME']).getOrCreate()
glueContext = GlueContext(spark)

# Initialize AWS Glue Job
job = Job(glueContext)
job.init(args['JOB_NAME'], args)  

# Define S3 Paths
INPUT_PATH = "s3://tiger-mle-pg/home/kajal.agarwal/housing.csv"
OUTPUT_PATH = "s3://tiger-mle-pg/home/kajal.agarwal/"

# Read Data
housing_df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)

# Define numerical and categorical attributes
num_attribs = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms", 
               "population", "households", "median_income"]
cat_attribs = ["ocean_proximity"]

# Handle missing values
columns_with_nulls = ['total_rooms', 'total_bedrooms', 'population', 'households', 'median_income']
imputer = Imputer(inputCols=columns_with_nulls, outputCols=columns_with_nulls)

# Encode categorical variable
indexer = StringIndexer(inputCol="ocean_proximity", outputCol="ocean_proximity_index")
encoder = OneHotEncoder(inputCol="ocean_proximity_index", outputCol="ocean_proximity_encoded")

# Feature Engineering
housing_df = housing_df.withColumn("rooms_per_household", col("total_rooms") / col("households"))
housing_df = housing_df.withColumn("bedrooms_per_room", col("total_bedrooms") / col("total_rooms"))
housing_df = housing_df.withColumn("population_per_household", col("population") / col("households"))

# Assemble Features
feature_cols = num_attribs + ["rooms_per_household", "bedrooms_per_room", "population_per_household"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features", handleInvalid="skip")

# Scale Features
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

# Define pipeline
pipeline = Pipeline(stages=[imputer, indexer, encoder, assembler, scaler])
housing_prepared = pipeline.fit(housing_df).transform(housing_df)

# Split data into train and test sets
train_data, test_data = housing_prepared.randomSplit([0.8, 0.2], seed=42)

# Train a Linear Regression Model
lr = LinearRegression(featuresCol="scaled_features", labelCol="median_house_value")
lr_model = lr.fit(train_data)

# Make predictions on test data
predictions = lr_model.transform(test_data)

# Save model metrics to S3
model_summary = {
    "RMSE": lr_model.summary.rootMeanSquaredError,
    "r2": lr_model.summary.r2,
    "MAE": lr_model.summary.meanAbsoluteError
}

print(f"Model Performance: RMSE={model_summary['RMSE']}, R2={model_summary['r2']}, MAE={model_summary['MAE']}")

# Save predictions
predictions.select("scaled_features", "median_house_value", "prediction").write.mode("overwrite").parquet(OUTPUT_PATH + "predictions")

# Commit AWS Glue Job
job.commit()
