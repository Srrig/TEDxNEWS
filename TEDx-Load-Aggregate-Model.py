import sys
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, collect_list, array_join
from pyspark.sql.types import StringType, StructType, StructField, ArrayType
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import requests
import re

# Percorsi ai file
tedx_dataset_path = "s3://tedx-2024-dataruggeri/final_list.csv"
details_dataset_path = "s3://tedx-2024-dataruggeri/details.csv"
related_videos_path = "s3://tedx-2024-dataruggeri/related_videos.csv"
tags_dataset_path = "s3://tedx-2024-dataruggeri/tags.csv"
output_path = "s3://tedx-2024-dataruggeri/output/tedx_with_tags.csv"

# Lettura dei parametri
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Inizializzazione del contesto Spark e Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Lettura dei file di input
tedx_dataset = spark.read.option("header", "true").csv(tedx_dataset_path).dropDuplicates().filter(col("id").isNotNull())
details_dataset = spark.read.option("header", "true").csv(details_dataset_path)
related_dataset = spark.read.option("header", "true").csv(related_videos_path)
tags_dataset = spark.read.option("header", "true").csv(tags_dataset_path)

# Unione dei dataset
details_dataset = details_dataset.select(col("id").alias("id_det"), "description", "duration", "publishedAt")
tedx_dataset_main = tedx_dataset.join(details_dataset, tedx_dataset["id"] == details_dataset["id_det"], "left").drop("id_det")

related_dataset = related_dataset.groupBy("id").agg(
    collect_list("related_id").alias("related_videos_id_list"),
    collect_list("title").alias("title_related_videos_list")
)
tedx_dataset_main = tedx_dataset_main.join(related_dataset, tedx_dataset_main["id"] == related_dataset["id"], "left").drop(related_dataset["id"])

tags_dataset_agg = tags_dataset.groupBy("id").agg(collect_list("tag").alias("tags"))
tedx_dataset_agg = tedx_dataset_main.join(tags_dataset_agg, tedx_dataset_main["id"] == tags_dataset_agg["id"], "left").drop(tags_dataset_agg["id"])

# Funzione per estrarre i tag via web scraping
def extract_tags(url):
    # Aggiunta di "http://" se l'URL non contiene un protocollo
    if not re.match(r'http[s]?://', url):
        url = 'http://' + url
    try:
        response = requests.get(url)
        content = response.text
        # regex per estrarre i tag dal contenuto della pagina
        tags = re.findall(r'<meta name="keywords" content="(.*?)"', content)
        return tags
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

# Estrazione dei tag dai video
urls = tedx_dataset_agg.select("url").distinct().rdd.flatMap(lambda x: x).collect()
tags_data = [(url, extract_tags(url)) for url in urls]

# Creazione di un DataFrame con i tag estratti
schema = StructType([StructField("url", StringType(), True), StructField("scraped_tags", ArrayType(StringType()), True)])
tags_df = spark.createDataFrame(tags_data, schema).withColumn("scraped_tags_str", array_join(col("scraped_tags"), ", "))

tedx_dataset_agg = tedx_dataset_agg.join(tags_df, "url", "left")
tedx_dataset_agg = tedx_dataset_agg.withColumn("related_videos_id_list_str", array_join(col("related_videos_id_list"), ", ")) \
                                   .withColumn("title_related_videos_list_str", array_join(col("title_related_videos_list"), ", ")) \
                                   .withColumn("tags_str", array_join(col("tags"), ", "))

# Selezione delle colonne necessarie per il file CSV
tedx_dataset_final = tedx_dataset_agg.select(
    "id", "slug", "speakers", "title", "url", "description", "duration", "publishedAt", 
    "related_videos_id_list_str", "title_related_videos_list_str", "tags_str", "scraped_tags_str"
)

# Visualizza il risultato finale
tedx_dataset_final.show()

# Scrittura del risultato finale in un file CSV
tedx_dataset_final.write.option("header", "true").csv(output_path)

# Scrittura dei dati nel DWH (MongoDB)
write_mongo_options = {
    "connectionName": "TEDx2024",
    "database": "unibg_tedx_2024",
    "collection": "tedx_data",
    "ssl": "true",
    "ssl.domain_match": "false"
}

from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_final, glueContext, "nested")
glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)

job.commit()













