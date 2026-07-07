from pathlib import Path
from config.log_config import logger

class SQLManager:

    @staticmethod
    def read(path: str, **kwargs) -> str:
        """
        Lee un archivo SQL y reemplaza variables.

        Ejemplo:
            SELECT *
            FROM tabla
            WHERE fecha >= current_date()-{dias}
        """
        path_ = Path(path)

        if not path_.exists():
            raise FileNotFoundError(path)

        logger.info("Leyendo SQL %s", path)

        sql = path_.read_text(
            encoding="utf8"
        )

        if kwargs:
            sql = sql.format(**kwargs)

        return sql
