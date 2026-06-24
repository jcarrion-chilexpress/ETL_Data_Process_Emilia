# config/config.py
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ==================================================
    # Databricks (para ejecución local vía REST API)
    # ==================================================
    databricks_server_hostname: str = ""
    databricks_token: Optional[SecretStr] = None
    databricks_http_path: str = ""
    tabla_dashboard: str = (
        "adl_sandbox.cmontenegroo.emilia_dashboard_base"
    )
    default_notebook_path: str = ""

    # ==================================================
    # Paths
    # ==================================================
    base_path: Path = BASE_DIR
    data_path: Path = BASE_DIR / "data"
    logs_path: Path = BASE_DIR / "logs"
    config_path: Path = BASE_DIR / "config"
    # ==================================================
    # Logging
    # ==================================================
    archivo_log: str = "ETL_Data_Process_Emilia"
    # ==================================================
    # Pydantic
    # ==================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ==================================================
    # Archivos
    # ==================================================

    @property
    def salida_default(self) -> Path:
        return self.data_path / "sentimientos_pbi.parquet"

    @property
    def datos_default(self) -> Path:
        return self.data_path / "emilia_dashboard_base.parquet"

    # ==================================================
    # Entorno
    # ==================================================

    @property
    def es_databricks(self) -> bool:
        try:
            from pyspark.sql import SparkSession
            return SparkSession.getActiveSession() is not None

        except Exception:
            return False

    @property
    def cluster_id(self) -> Optional[str]:
        if not self.es_databricks:
            return None
        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.getActiveSession()

            return spark.conf.get(
                "spark.databricks.clusterUsageTags.clusterId",
                None,
            )

        except Exception:
            return None

    @property
    def workspace_url(self) -> Optional[str]:

        if not self.es_databricks:
            return None

        try:
            from pyspark.sql import SparkSession

            spark = SparkSession.getActiveSession()

            return spark.conf.get(
                "spark.databricks.workspaceUrl",
                None,
            )

        except Exception:
            return None


@lru_cache
def get_settings() -> Settings:
    return Settings()


get_settings()

