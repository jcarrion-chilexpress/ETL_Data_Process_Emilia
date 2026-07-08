CREATE TABLE IF NOT EXISTS adl_sandbox.ext_jcarrion.t_emilia_dashboard_base (
    session_id STRING,
    id STRING,
    message_date DATE,
    expires_at TIMESTAMP,
    updated_at TIMESTAMP,
    history ARRAY<
        STRUCT<
            role: STRING,
            content: STRING,
            timestamp: STRING
        >
    > NOT NULL,
    primer_timestamp STRING,
    ultimo_timestamp STRING,
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    cantidad_mensajes INT NOT NULL,
    mensajes_usuario INT NOT NULL,
    mensajes_bot INT NOT NULL,
    turnos_conversacion DECIMAL(13,1),
    tipo_sesion STRING NOT NULL,
    duracion_minutos DECIMAL(24,2),
    duracion_segundos BIGINT,
    orden_conv INT NOT NULL,
    orden_enc INT,
    fecha_encuesta TIMESTAMP,
    eval_ia INT,
    eval_acceso INT,
    resolucion STRING,
    id_reclamo STRING,
    pidio_datos BIGINT,
    solicitud_creacion_reclamo BIGINT,
    genero_caso INT,
    error_reclamos BIGINT,
    estado_reclamo STRING,
    isn DECIMAL(27,2),
    fecha_carga TIMESTAMP,
    
        CONSTRAINT pk_adl_sandbox_ext_jcarrion_t_emilia_dashboard_base
        PRIMARY KEY (session_id,message_date,primer_timestamp) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;
---------------------------------------------------------------

CREATE TABLE IF NOT EXISTS adl_sandbox.ext_jcarrion.t_sentimientos_emilia (
    session_id STRING,
    message_date DATE,
    sentiment STRING,
    confidence DOUBLE,
    messages BIGINT,
    fecha_carga TIMESTAMP NOT NULL,

    CONSTRAINT pk_adl_sandbox_ext_jcarrion_t_sentimientos_emilia
        PRIMARY KEY (session_id,message_date) NOT ENFORCED
)
USING DELTA
CLUSTER BY AUTO;

