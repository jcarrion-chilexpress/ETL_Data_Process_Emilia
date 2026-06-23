from pathlib import Path
import pandas as pd
from config.config import get_settings
from config.log_config import logger

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


def crear_directorios() -> tuple[bool,str]:
    try:
        for path in (
            get_settings().data_path,
            get_settings().logs_path,
            get_settings().config_path,
        ):
            path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Directorios Base creados exitosamente')
        return True,"Directorios Base creados exitosamente"

    except Exception as e:
        logger.error(f'Error al crear directorios Base {e}')
        return False,"Error al crear directorios Base {e}"
