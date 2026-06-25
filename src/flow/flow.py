from pathlib import Path
from src.utils.utils import read_json_file,read_sql_file
from config.config import get_settings
from config.log_config import logger
from src.load.export_sentimientos_pbi import (
    orquestador
)

settings = get_settings()

def step_get_sqlquery(table_name:str):
    json_file = settings.config_path
    file_name = table_name

    logger.info(f'Cargando query {json_file}{file_name}')
    msn, archivo = read_json_file(
                                json_file,
                                file_name)

    if not msn:
        logger.error(f"Error Leyendo json {json_file}")
        return False, ""

    logger.info(f'Archivo Json {archivo} cargado exitosamente')
    sql_path = archivo["query_sql_path"]
    filtro   = archivo["filtro"]

    success,sql_query = read_sql_file(sql_path
                                        ,dias=filtro)
    if not success:
        logger.error(f'Error Leyendo {sql_query}')
        return False,''

    logger.info(f'Query {table_name} ok')
    return True,sql_query


def step_generar_pdf(query:str
                     ,file_name:str):
    pdf = orquestador(query,file_name)
    return pdf

def step_create_table_Databricks(pdf):
    pdf.to_parquet(settings.salida_default)
    df_spark = spark.createDataFrame(pdf)
    df_spark.write.mode("overwrite").saveAsTable(
        "adl_sandbox.ext_jcarrion.vw_sentimientos_emilia")

