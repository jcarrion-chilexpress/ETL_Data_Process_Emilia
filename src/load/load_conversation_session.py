from pyspark.sql import DataFrame
import pandas as pd
from pyspark.sql.functions import (
                                    col,
                                    from_json,
                                    get_json_object,
                                    posexplode,
                                    to_timestamp,
                                    lit)
from pyspark.sql.types import (
                                ArrayType,
                                StructField,
                                StructType,
                                StringType)
from datetime import datetime,timedelta
from config.log_config import logger

# ------------------------------------------------------------ #
# Schema de all_history
# ------------------------------------------------------------ #

history_schema = ArrayType(
    StructType(
        [
            StructField("role", StringType(), True),
            StructField("content", StringType(), True),
            StructField("timestamp", StringType(), True),
        ]
    )
)

# ------------------------------------------------------------ #
def unpack_conversations(
    df: DataFrame,
    dia_desde: int = 0,
)-> DataFrame: 
    """
    Desempaqueta la columna documento_json_crudo y genera un DataFrame
    con un registro por mensaje.

    Parameters
    ----------
    df : DataFrame
        DataFrame origen.
    fecha_desde : str, optional
        Fecha mínima (YYYY-MM-DD).

    Returns
    -------
    DataFrame
    """
    logger.info('Generando desde unpack_conversations')
    fecha = (datetime.now() + timedelta(days=-int(dia_desde))).date()
    try:
        resultado = (
            df
        .select(
            "session_id",
            get_json_object("documento_json_crudo", "$.dialog_state").alias("dialog_state"),
            get_json_object("documento_json_crudo", "$.updated_at.$date").alias("conversation_updated_at"),
            get_json_object("documento_json_crudo", "$.expires_at.$date").alias("conversation_expires_at"),
            from_json(
                get_json_object("documento_json_crudo", "$.all_history"),
                history_schema,
            ).alias("all_history"),
        )
        .select(
            "session_id",
            "dialog_state",
            "conversation_updated_at",
            "conversation_expires_at",
            posexplode("all_history").alias("message_index", "message"),
        )
        .select(
            col("session_id"),
            col("dialog_state"),
            to_timestamp("conversation_updated_at").alias("conversation_updated_at"),
            to_timestamp("conversation_expires_at").alias("conversation_expires_at"),
            col("message_index"),
            col("message.role").alias("role"),
            col("message.content").alias("content"),
            to_timestamp(col("message.timestamp")).alias("message_timestamp"),
            )
        )

        if fecha:
            resultado = resultado.filter(
                col("message_timestamp") >= lit(fecha)
            )

        logger.info('DF unpack_conversations generado Exitosamente')
        return resultado
    
    except Exception as e:
        logger.error("Error al DF unpack_conversations %s",e)
        raise ValueError("Error al DF unpack_conversations %s",e)

