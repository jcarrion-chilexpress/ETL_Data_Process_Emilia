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
from src.utils.utils import (crear_directorios
                             ,save_parquet)
## ------------------------------- ##
SALIDA_DEFAULT= get_settings().salida_default
DATOS_DEFAULT =get_settings().datos_default
#####################################

settings = get_settings()

def cargar_datos(query) -> pd.DataFrame:
    from src.infra.databricks_client import cargar_dashboard_base, configurado
    if not configurado():
        raise SystemExit(
            "Sin datos locales ni Databricks configurado.\n"
            "Usa --datos <parquet|csv> o configura .env (DATABRICKS_*)."
        )
    return cargar_dashboard_base(query)

def cargar_sentimientos_emilia(pdf) -> pd.DataFrame:
    if "history" not in pdf.columns:
        logger.error("El dataset debe tener columna history")
        raise ValueError(
            "El dataset debe tener columna history")

    rows = pdf_a_dashboard(pdf)
    pbi = pd.DataFrame(
        [
            {
                "session_id": r["id"],
                "fecha": r["date"],
                "sentiment": r["sentiment"],
                "confidence": r["confidence"],
                "messages": r["messages"],
            }
            for r in rows
        ]
    )
    logger.info("Dataset sentimientos emilia ok")
    return pbi

def orquestador(
    query: str = "",
    file_name: str = "",
    file_save: bool = False
) -> tuple[bool, pd.DataFrame]:

    try:
        crear_directorios()
        pdf = cargar_datos(query)
        if file_name == settings.tabla_sentimientos_emilia:
            pdf = cargar_sentimientos_emilia(pdf)

        if file_save:
            save_parquet(pdf,file_name)

        return True, pdf

    except Exception as e:
        logger.exception(e)
        return False, pd.DataFrame()
    
