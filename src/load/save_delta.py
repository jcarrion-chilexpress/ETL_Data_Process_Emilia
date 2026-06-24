from pyspark.sql import SparkSession

from config.config import get_config
from config.log_config import logger

config = get_config()

def guardar_delta_merge(
  sdf,
  table_name:str):

  logger.info(f'Nombre Tabla : {table_name}')
  logger.info(f'pdf data\n : {sdf}')

  spark = SparkSession.getActiveSession()

  sdf = spark.createDataFrame(sdf)

  sdf.createOrReplaceTempView(
      "tmp_sentimientos")

  spark.sql(f"""
      MERGE INTO {table_name} tgt
      USING tmp_sentimientos src
      ON tgt.session_id = src.session_id

      WHEN MATCHED THEN
          UPDATE SET *

      WHEN NOT MATCHED THEN
          INSERT *
  """)
