###### TEDx-Load-Aggregate-Model ######

import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join
from pyspark.sql.types import StringType, StructType, StructField, ArrayType

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

import requests
import re

##### FROM FILES
tedx_dataset_path = "s3://tedx-2024-dataruggeri/final_list.csv"

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(tedx_dataset_path)

tedx_dataset.printSchema()

## Eliminazione dal dataset dei dati con id nullo e duplicati
tedx_dataset = tedx_dataset.filter(tedx_dataset["id"].isNotNull())
tedx_dataset = tedx_dataset.dropDuplicates()

## READ THE DETAILS
details_dataset_path = "s3://tedx-2024-dataruggeri/details.csv"
details_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(details_dataset_path)

details_dataset = details_dataset.select(col("id").alias("id_det"),
                                         col("description"),
                                         col("duration"),
                                         col("publishedAt"))

## JOIN TRA LE TABELLE
tedx_dataset_main = tedx_dataset.join(details_dataset, tedx_dataset.id == details_dataset.id_det, "left") \
    .drop("id_det")

## RELATED VIDEOS
related_videos_path = "s3://tedx-2024-dataruggeri/related_videos.csv"
related_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(related_videos_path)

## groupBy
related_dataset = related_dataset.groupBy(col("id").alias("id_path")).agg(collect_list("related_id") \
    .alias("related_videos_id_list"), collect_list("title").alias("title_related_videos_list"))

## JOIN RELATED VIDEOS
tedx_dataset_main = tedx_dataset_main.join(related_dataset, tedx_dataset_main.id == related_dataset.id_path, "left") \
    .drop("id_path") \
    .select(col("id").alias("id_related_videos"), col("*"))

## STAMPA A VIDEO
related_dataset.printSchema()
tedx_dataset_main.printSchema()

## READ TAGS DATASET
tags_dataset_path = "s3://tedx-2024-dataruggeri/tags.csv"
tags_dataset = spark.read.option("header", "true").csv(tags_dataset_path)

# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("id").alias("id_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset_main.join(tags_dataset_agg, tedx_dataset.id == tags_dataset_agg.id_ref, "left") \
    .drop("id_ref") \
    .select(col("id").alias("_id"), col("*")) \
    .drop("id")

tedx_dataset_agg.printSchema()

### Web scraping dei tag
def extract_tags(url):
    response = requests.get(url)
    content = response.text
    # Usa regex per estrarre i tag dal contenuto della pagina
    tags = re.findall(r'<meta name="keywords" content="(.*?)"', content)
    return tags

# Esempio di URL di un talk TEDx (dinamico essendo in un'applicazione reale)
urls = tedx_dataset_agg.select("url").distinct().rdd.flatMap(lambda x: x).collect()
tags_data = [(url, extract_tags(url)) for url in urls]

# Aggiunta tag estratti al dataset con schema esplicito
schema = StructType([
    StructField("url", StringType(), True),
    StructField("scraped_tags", ArrayType(StringType()), True)  # Rinominato a scraped_tags
])
tags_df = spark.createDataFrame(tags_data, schema)

# Conversione colonne di tipo array in stringa
tags_df = tags_df.withColumn("scraped_tags_str", array_join(col("scraped_tags"), ", "))

# join con il DataFrame aggregato
tedx_dataset_agg = tedx_dataset_agg.join(tags_df.select("url", "scraped_tags_str"), "url", "left")

# Conversione altre colonne di tipo array in stringa
tedx_dataset_agg = tedx_dataset_agg.withColumn("related_videos_id_list_str", array_join(col("related_videos_id_list"), ", ")) \
                                   .withColumn("title_related_videos_list_str", array_join(col("title_related_videos_list"), ", ")) \
                                   .withColumn("tags_str", array_join(col("tags"), ", "))

# Selezione colonne necessarie per il CSV, escludendo quelle di tipo array originali
tedx_dataset_final = tedx_dataset_agg.select("_id", "id_related_videos", "slug", "speakers", "title", "url", "description", "duration", "publishedAt",
                                             "related_videos_id_list_str", "title_related_videos_list_str", "tags_str", "scraped_tags_str")

# Visualizza il risultato finale
tedx_dataset_final.show()

# Scrittura del risultato finale in un file CSV
output_path = "s3://tedx-2024-dataruggeri/output/tedx_with_tags.csv"
tedx_dataset_final.write.option("header", "true").csv(output_path)

# Scrittura dati nel DWH (MongoDB)
write_mongo_options = {
    "connectionName": "TEDx2024",
    "database": "unibg_tedx_2024",
    "collection": "tedx_data",
    "ssl": "true",
    "ssl.domain_match": "false"}

from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_final, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)

job.commit()
