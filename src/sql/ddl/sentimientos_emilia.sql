CREATE TABLE IF NOT EXISTS {full_name} (
    session_id STRING,
    message_date DATE,
    sentiment STRING,
    confidence DOUBLE,
    messages BIGINT,
    fecha_carga TIMESTAMP NOT NULL,

    CONSTRAINT pk_{constraint_pk}
        PRIMARY KEY ({primary_key}) NOT ENFORCED
)
USING DELTA
{partition_by};
