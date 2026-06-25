from pathlib import Path
import pandas as pd
from src.utils.utils import read_json_file,read_sql_file
from config.config import get_settings
from config.log_config import logger
from src.load.export_sentimientos_pbi import (
    orquestador
)

settings = get_settings()
sanbox = settings.default_sandbox

def step_get_sqlquery(table_name:str):
    json_file = settings.config_path
    file_name = table_name

    logger.info(f'Cargando query {json_file}{file_name}')
    msn, archivo = read_json_file(
                                json_file,
                                file_name)

    if not msn:
        logger.error(f"Error Leyendo json {json_file}")
        return False,'tabla_sql','query_vacia'

    logger.info(f'Archivo Json {archivo} cargado exitosamente')
    sql_path  = archivo["query_sql_path"]
    filtro    = archivo["filtro"]
    tabla_sql = archivo["tabla_sql"]

    success,sql_query = read_sql_file(sql_path
                                        ,dias=filtro)
    if not success:
        logger.error(f'Error Leyendo {sql_query}')
        return False,'tabla_sql','query_vacia'

    logger.info(f'Query {table_name} ok')
    return True,tabla_sql,sql_query


def step_generar_pdf(query: str, file_name: str,file_save=False):
    success, pdf = orquestador(query
                               ,file_name
                               ,file_save=file_save)

    if not success:
        logger.error("No fue posible generar el DataFrame.")
        return False, None

    return True, pdf

def step_save_table(spark, df, tabla):
    try:
        logger.info(f'Creando tabla {sanbox}.{tabla}')
        df_spark = spark.createDataFrame(df)
        if isinstance(df, pd.DataFrame):
            df = spark.createDataFrame(df)
            (
                df_spark.write
                .mode("overwrite")
                .saveAsTable(f"{sanbox}.{tabla}")
            )
            logger.info(f'Tabla {sanbox}.{tabla} creada exitosamente')
    except Exception as e:
        logger.exception(e)
