## src/flow/flow.py
from pathlib import Path
import pandas as pd
from src.utils.utils import (get_fecha_carga
                             ,read_sql_file
                             ,read_parquet)
from config.config import get_settings
from config.log_config import logger
from src.transform.consolidado_reclamos import crear_resumen_reclamos
from src.load.orquestador_carga import (
    orquestador
)
from src.catalog.catalog_manager import get_catalogo_manager

from pyspark.sql.functions import lit
### -------------------------------- ###
settings = get_settings()
sanbox = settings.default_sandbox
### -------------------------------- ###

def step_generar_dfs_sql(spark, table_name:str):
    try:
        logger.info(f' Generando DFS de las tabla :{table_name}')
        catalogo = get_catalogo_manager()

        tabla = catalogo.obtener_tabla(table_name)
        sql   = tabla.query_sql_path
        sql_where = tabla.where
        msn,sql_query = read_sql_file(file_path=sql
                                  ,dias=sql_where)

        if not msn:
            raise ValueError('Error leyendo SQL FILE')

        dfs = spark.sql(sql_query)
        dfs = dfs.withColumn('fecha_carga'
                             ,lit(get_fecha_carga()))
        return dfs

    except Exception as e:
        logger.error('Error Generando DFS :%s',{e})
        return spark.sql()


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

def step_create_BD_reclamos(spark,load_table:bool = False):
    logger.info(f'Creando tabla de reclamos')
    success,archivos = crear_resumen_reclamos()
    path_reclamos = settings.reclamos_path

    try:
        if success:
            for archivo in archivos:
                parquet = read_parquet(archivo,path_reclamos)
                nombre_tabla = 'reclamos_'+archivo

                if load_table:
                    step_save_table(spark,parquet,nombre_tabla)
    except Exception as e:
        logger.exception(f'Error Creando tabla de reclamos !: {e}')

