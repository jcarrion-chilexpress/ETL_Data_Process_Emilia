import json
from typing import Any
from pathlib import Path
import pandas as pd
from config.config import get_settings
from config.log_config import logger

settings = get_settings()

# -------------------------------------------------- #
def save_parquet(df:pd.DataFrame,file_name:str,path_file:Path|None = None):
    if path_file is None:
        path_file = settings.data_path

    path_parquet = Path(path_file, file_name+".parquet")
    try:
        logger.info(f'Guardando archivo {path_parquet}')
        df.to_parquet(path_parquet)
    except Exception as e:
        logger.exception(f'Error guardando Parquet{e}')


def leer_parquet(file: str | Path) -> pd.DataFrame:
    """
    Lee un archivo parquet y devuelve un DataFrame.
    Parameters
    ----------
    file : str | Path
        Ruta/Nombre del archivo parquet.
    Returns
    -------
    pd.DataFrame
    """
    ruta = Path(get_settings().data_path,file)
    logger.info(f'Leyendo archivo {ruta}')
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {ruta}"
        )

    return pd.read_parquet(ruta)

# -------------------------------------------------- #
def crear_directorios() -> tuple[bool,str]:
    try:
        for path in (
            get_settings().data_path,
            get_settings().logs_path,
            get_settings().config_path,
            get_settings().reclamos_path):

            if path.exists():
                continue
            else:
                path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Directorios Base creados exitosamente')
        return True,"Directorios Base creados exitosamente"

    except Exception as e:
        logger.exception(f'Error al crear directorios Base {e}')
        return False,"Error al crear directorios Base {e}"


# -------------------------------------------------- #
def read_sql_file(file_path: str, **kwargs) -> tuple[bool, str]:
    """
    file_path: Path del archivo SQL
    kwargs : recibe el columna_nombre = filtro
    """
    try:
        if not file_path:
            logger.error(
            "No existe query_sql_path en el archivo json")

        if not Path(file_path).is_file():
            logger.error("El archivo %s no existe.", file_path)
            return False, ""

        with open(file_path, "r", encoding="utf-8") as file:
            sql = file.read()

        if kwargs:
            sql = sql.format(**kwargs)

        logger.info("El archivo %s existe.", file_path)
        return True, sql

    except Exception as e:
        logger.exception("Error al leer SQL: %s", e)
        return False, ""

# -------------------------------------------------- #
def read_json_file(
    file_path: Path,
    file_name: str | None = None
    ) -> tuple[bool, dict[str, Any]]:
    try:
        if not Path(file_path).is_file():
            logger.error("El archivo JSON no existe: %s", file_path)
            return False, {}

        logger.info("El archivo JSON existe: %s", file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        # Si no se solicita una clave específica,
        # retorna todo el contenido del JSON.
        if file_name is None:
            return True, data

        # Busca la clave solicitada.
        json_key = data.get(file_name)
        if json_key is None:
            logger.warning(
                "La clave '%s' no existe en el archivo %s",
                file_name,
                file_path
            )
            return False, {}

        return True, json_key

    except Exception as e:
        logger.exception("Error al leer archivo JSON: %s", e)
        return False, {}

