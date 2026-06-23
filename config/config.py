#config/config.py
from typing import Optional
from pydantic import Field,SecretStr
from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    databricks_server_hostname: str = Field(default="")
    databricks_token:Optional[SecretStr] = Field(default=None)
    databricks_http_path:str        = Field(default="")

    ###################################################
    base_path:Path = Path.cwd()
    data_path:Path = base_path / 'data'
    data_parquet_output:Path  = data_path
    salida_default:Path       = data_path / "sentimientos_pbi.parquet"
    datos_default:Path        = data_path / "emilia_dashboard_base.parquet"
    ###################################################

    tabla_dashboard:str  = Field(default="")
    default_notebook_path:str  = Field(default="")

    ###################################################
    archivo_log: str = Field(default="app")
    ###################################################
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()


