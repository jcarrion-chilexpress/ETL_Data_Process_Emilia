SELECT
session_id,
id,
fecha,
history,
fecha_inicio,
fecha_fin,
cantidad_mensajes,
mensajes_usuario,
mensajes_bot,
tipo_sesion,
duracion_minutos,
isn
FROM adl_sandbox.cmontenegroo.emilia_dashboard_base
where fecha >= current_date()-{dias}



