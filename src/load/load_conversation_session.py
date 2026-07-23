### ----------------------------------------------- ###
from datetime import datetime, timedelta
from pyspark.sql.functions import (
                                    from_json,
                                    col,
                                    get_json_object,
                                    to_timestamp,
                                    posexplode,
                                    coalesce)
from pyspark.sql.types import (
                                ArrayType,
                                StructType,
                                StructField,
                                StringType)

history_schema = ArrayType(
    StructType([
        StructField("role", StringType()),
        StructField("content", StringType()),
        StructField("timestamp", StringType()),
    ])
)
from config.log_config import logger

def unpack_conversations(dfs,dia_desde:int = 0):
    logger.info('Ejecutando unpack_conversations')
    fecha_desde = (
            datetime.now() +
            timedelta(days=-dia_desde)
        ).date()

    try:
        df_exploded = (
            dfs
            .select(
                "session_id",
                # Campos existentes
                get_json_object("documento_json_crudo", "$.dialog_state").alias("dialog_state"),
                get_json_object("documento_json_crudo", "$.last_message_time").alias("last_message_time"),

                # Nuevos campos
                coalesce(
                    to_timestamp(get_json_object("documento_json_crudo", "$.expires_at")),
                    to_timestamp(get_json_object("documento_json_crudo", "$.expires_at.$date"))
                ).alias("expires_at"),

                coalesce(
                    to_timestamp(get_json_object("documento_json_crudo", "$.updated_at")),
                    to_timestamp(get_json_object("documento_json_crudo", "$.updated_at.$date"))
                ).alias("updated_at"),

                # Conversación completa
                from_json(
                    get_json_object("documento_json_crudo", "$.all_history"),
                    history_schema
                ).alias("all_history")
            )
            .select(
                "session_id",
                "dialog_state",
                "last_message_time",
                "expires_at",
                "updated_at",
                posexplode("all_history").alias("message_index", "message")
            )
            .select(
                "session_id",
                "dialog_state",
                "last_message_time",
                col("expires_at").alias("conversation_expires_at"),
                col("updated_at").alias("conversation_updated_at"),
                "message_index",
                col("message.role").alias("role"),
                col("message.content").alias("content"),
                to_timestamp(col("message.timestamp")).alias("message_timestamp")
            )
            .filter(col("message_timestamp") >= fecha_desde)
        )
        logger.info('Ejecución de unpack_conversations Exitosa')
        return df_exploded
    except Exception as e:
        raise ValueError("Ejecución de unpack_conversations Exitosa %s",e)