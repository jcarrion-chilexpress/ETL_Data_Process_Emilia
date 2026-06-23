from pathlib import Path
import pandas as pd
from config.config import settings
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
    ruta = Path(settings.data_parquet_output,file)

    logger.info(f'Leyendo archivo {ruta}')

    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {ruta}"
        )

    return pd.read_parquet(ruta)


