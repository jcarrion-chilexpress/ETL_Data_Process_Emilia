### src/load/export_sentimientos_pbi.py
"""
Exporta conversaciones clasificadas para Power BI.
  python export_sentimientos_pbi.py
  python export_sentimientos_pbi.py --desde 2025-01-01 --hasta 2025-06-15
  python export_sentimientos_pbi.py --datos data/emilia_dashboard_base.parquet
  python export_sentimientos_pbi.py --csv
"""
from __future__ import annotations
import argparse
from typing import Any
import pandas as pd
from pathlib import Path
#####################################
from src.transform.bot_emilia_sentimientos import pdf_a_dashboard

from config.config import get_settings
from config.log_config import logger
from src.catalog.sql_manager import SQLManager
from src.utils.utils import (crear_directorios)
## ------------------------------- ##
from src.infra.databricks_client import cargar_dashboard_base, configurado
## ------------------------------- ##
SALIDA_DEFAULT= get_settings().salida_default
DATOS_DEFAULT =get_settings().datos_default
#####################################

settings = get_settings()

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

def cargar_datos(spark,table) -> pd.DataFrame:

    logger.info('Cargando datos Sent EMilia')
    query = SQLManager.read(
        table.query_sql_path,
        dias=table.where)
    
    logger.info(f"desde SQL {table.query_sql_path}")

    dfs = cargar_dashboard_base(query)
    pdf = cargar_sentimientos_emilia(dfs)
    return pdf
