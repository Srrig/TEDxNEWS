import sys
import pyspark
from pyspark.sql.functions import col, collect_list, array_contains

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

#### READ INPUT FILES TO CREATE AN INPUT DATASET

# Read final_list.csv
final_list_path = "s3://tedx-2024-data-ruggeri/final_list.csv"
final_list_df = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(final_list_path) \
    .select(col("id").alias("video_id"),
            col("slug"),
            col("speakers"),
            col("title"),
            col("url"))

# Read details.csv
details_path = "s3://tedx-2024-data-ruggeri/details.csv"
details_df = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(details_path) \
    .select(col("id").alias("detail_id"),
            col("description"),
            col("duration"),
            col("socialDescription"),
            col("presenterDisplayName"),
            col("publishedAt"))

# Read images.csv
images_path = "s3://tedx-2024-data-ruggeri/images.csv"
images_df = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(images_path) \
    .select(col("id").alias("image_id"),
            col("url").alias("image_url"))

# Read related_videos.csv
related_videos_path = "s3://tedx-2024-data-ruggeri/related_videos.csv"
related_videos_df = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(related_videos_path) \
    .select(col("id").alias("related_id"),
            col("related_id").alias("related_video_id"),
            col("title").alias("related_video_title"))

# Read tags.csv
tags_path = "s3://tedx-2024-data-ruggeri/tags.csv"
tags_df = spark.read \
    .option("header", "true") \
    .csv(tags_path) \
    .select(col("id").alias("tag_id"),
            col("tag"))

#### JOIN DATASETS

# Join final_list with details
main_df = final_list_df.join(details_df, final_list_df.video_id == details_df.detail_id, "left") \
    .drop("detail_id")

# Join with images
main_df = main_df.join(images_df, main_df.video_id == images_df.image_id, "left") \
    .drop("image_id")

# Join with tags
tags_agg = tags_df.groupBy(col("tag_id")).agg(collect_list("tag").alias("tags"))
main_df = main_df.join(tags_agg, main_df.video_id == tags_agg.tag_id, "left") \
    .drop("tag_id")

# Join with related videos
related_videos_agg = related_videos_df.groupBy(col("related_id")).agg(
    collect_list("related_video_id").alias("related_videos_id_list"),
    collect_list("related_video_title").alias("title_related_videos_list")
)
main_df = main_df.join(related_videos_agg, main_df.video_id == related_videos_agg.related_id, "left") \
    .drop("related_id")

#### FILTER DATA BASED ON TAGS

required_tags = ["society", "politics", "economics", "health", "sustainability"]
filtered_df = main_df.filter(
    col("tags").isNotNull() & (
        array_contains(col("tags"), required_tags[0]) |
        array_contains(col("tags"), required_tags[1]) |
        array_contains(col("tags"), required_tags[2]) |
        array_contains(col("tags"), required_tags[3]) |
        array_contains(col("tags"), required_tags[4])
    )
)

# Remove duplicates if any
filtered_df = filtered_df.dropDuplicates()

# Print schema to verify
filtered_df.printSchema()

# Write to MongoDB
write_mongo_options = {
    "connectionName": "TEDx2024",
    "database": "unibg_tedx_2024",
    "collection": "watch_next",
    "ssl": "true",
    "ssl.domain_match": "false"
}

from awsglue.dynamicframe import DynamicFrame
filtered_dynamic_frame = DynamicFrame.fromDF(filtered_df, glueContext, "nested")
glueContext.write_dynamic_frame.from_options(filtered_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)