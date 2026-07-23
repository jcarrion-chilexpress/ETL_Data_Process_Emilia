### src/load/load_data_emilia.py
"""
Exporta conversaciones clasificadas para Power BI.
"""
from __future__ import annotations
import argparse
from typing import Any
import pandas as pd
from pathlib import Path
#####################################
from src.transform.bot_emilia_sentimientos import pdf_a_dashboard
from pyspark.sql import DataFrame
from config.config import get_settings
from config.log_config import logger
from src.catalog.sql_manager import SQLManager
from src.utils.utils import (crear_directorios)
## ------------------------------- ##
from src.infra.databricks_client import cargar_dashboard_base, configurado
from src.load.load_conversation_session import unpack_conversations
## ------------------------------- ##
SALIDA_DEFAULT= get_settings().salida_default
DATOS_DEFAULT =get_settings().datos_default
#####################################

settings = get_settings()

#####################################
def get_conversations_dataframe(spark,table):
    logger.info('Gnerando DF con desde chilexpress_bot_conversation_sessions')
    df = spark.table(
        table.origen_datos)

    logger.info(f'Se genero vista temporal : {table.view_temp}')

    return unpack_conversations(
        df,
        dia_desde=table.where,
    )

#####################################
def cargar_sentimientos_emilia(pdf) -> pd.DataFrame:
    logger.info('Gnerando DF con Sent EMilia')
    if "history" not in pdf.columns:
        logger.error("El dataset debe tener columna history")
        raise ValueError(
            "El dataset debe tener columna history")

    rows = pdf_a_dashboard(pdf)
    pbi = pd.DataFrame(
        [
            {
                "session_id": r["id"],
                "message_date": r["date"],
                "sentiment": r["sentiment"],
                "confidence": r["confidence"],
                "messages": r["messages"],
            }
            for r in rows
        ]
    )
    logger.info("Dataset sentimientos emilia ok")
    return pbi

#####################################
def cargar_datos(spark,table) -> pd.DataFrame:
    logger.info('Cargando datos Sent EMilia')
    query = SQLManager.read(
        table.query_sql_path,
        dias=table.where)
    
    logger.info(f"desde SQL {table.query_sql_path}")

    dfs = cargar_dashboard_base(query)
    pdf = cargar_sentimientos_emilia(dfs)
    return pdf

#####################################
def cargar_datos_dashboard_base(spark,table) -> DataFrame|None:
    logger.info('Cargando datos dashboard base!')

    try:
        dfs = get_conversations_dataframe(spark,table)
        dfs.createOrReplaceTempView(table.view_temp)

        Q_datos = dfs.count()
        logger.info(f'Vista Temporal {table.view_temp} Creada con {Q_datos} Registros!')
        query = SQLManager.read(
            table.query_sql_path,
            view_temp= table.view_temp,
            dias=table.where)

        df_temp = SQLManager.execute(spark
                                    ,sql = query)

        logger.info(f"desde SQL {table.query_sql_path}")
        return df_temp
    except Exception as e:
        logger.exception("Error al Generar Dashoard Base %s",e)

