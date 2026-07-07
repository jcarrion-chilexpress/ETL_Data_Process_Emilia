CREATE TABLE IF NOT EXISTS {full_name} (
    session_id STRING,
    id STRING,
    message_date DATE,

    history ARRAY<
        STRUCT<
            content: STRING,
            role: STRING,
            timestamp: STRING
        >
    >,

    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,

    cantidad_mensajes INT,
    mensajes_usuario INT,
    mensajes_bot INT,

    tipo_sesion STRING,

    duracion_minutos DECIMAL(6,2),

    isn DECIMAL(3,1) NOT NULL,
    current_timestamp() as fecha_carga
)
USING DELTA;