### emilia_dashboard_sentimientos.py
"""
Genera dashboard_sentimientos.html desde un DataFrame de conversaciones (Databricks).
Basado en generar_dashboard_sentimientos.py del proyecto Emilia_aks.
"""
from __future__ import annotations
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import unquote
from config.log_config import logger
from src.utils.sentimientos_settings import (
                                KEYWORDS,URGENCY_PATTERNS
                                ,CONFUSION_PATTERNS,SATISFACTION_PATTERNS
                                ,FRUSTRACION,LOOP_TRACKING
                                ,BOT_PIDE_OT,ERROR_BOT_PATTERNS)

_PCT = re.compile(r"%[0-9A-Fa-f]{2}")

def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def similar(a: str, b: str, threshold: float = 0.82) -> bool:
    if not a or not b:
        return False
    return SequenceMatcher(None, norm(a), norm(b)).ratio() >= threshold


def decodificar_texto(texto: str | None) -> str:
    if not texto:
        return ""
    s = str(texto)
    if not _PCT.search(s):
        return s
    actual = s
    for _ in range(3):
        if not _PCT.search(actual):
            break
        try:
            siguiente = unquote(actual, encoding="utf-8", errors="strict")
        except (UnicodeDecodeError, ValueError):
            break
        if siguiente == actual:
            break
        actual = siguiente
    return actual


def normalizar_conversacion(conversacion: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalizada: list[dict[str, Any]] = []
    for msg in conversacion:
        copia = dict(msg)
        if copia.get("content") is not None:
            copia["content"] = decodificar_texto(copia.get("content"))
        normalizada.append(copia)
    return normalizada


def history_a_lista(history: Any) -> list[dict[str, Any]]:
    if history is None:
        return []
    if isinstance(history, str):
        try:
            history = json.loads(history)
        except json.JSONDecodeError:
            return []
    out: list[dict[str, Any]] = []
    for m in history:
        if hasattr(m, "asDict"):
            m = m.asDict()
        if not isinstance(m, dict):
            continue
        out.append(
            {
                "role": m.get("role"),
                "content": m.get("content", "") or "",
                "timestamp": m.get("timestamp", "") or "",
            }
        )
    return out


def detectar_quiebres(conversacion: list[dict[str, Any]]) -> list[str]:
    conv = {"conversacion": conversacion}
    quiebres: list[str] = []
    msgs = conv.get("conversacion") or []
    user_msgs = [norm(m.get("content", "")) for m in msgs if m.get("role") == "user"]
    asst_msgs = [norm(m.get("content", "")) for m in msgs if m.get("role") == "assistant"]

    for i, u1 in enumerate(user_msgs):
        if len(u1) < 8:
            continue
        for u2 in user_msgs[i + 1 :]:
            if similar(u1, u2):
                quiebres.append("loop_mensaje_usuario_repetido")
                break

    tracking_user = sum(1 for u in user_msgs if any(re.search(p, u) for p in LOOP_TRACKING))
    if tracking_user >= 2:
        quiebres.append("iteracion_consulta_tracking")

    ot_asks = sum(
        1
        for a in asst_msgs
        if "orden de transporte" in a or "número de ot" in a or "numero de ot" in a
    )
    if ot_asks >= 2:
        quiebres.append("loop_bot_solicita_ot")

    blob_user = " ".join(user_msgs)
    if any(re.search(p, blob_user) for p in FRUSTRACION):
        quiebres.append("senal_frustracion_cliente")

    blob_all = " ".join(asst_msgs)
    if "tienda donde" in blob_all or "vendedor" in blob_all:
        if any(re.search(r"\bsi\b", u) for u in user_msgs) and any(
            "reclamo" in u or "retras" in u for u in user_msgs
        ):
            quiebres.append("quiebre_derivacion_buyer_sin_resolucion")

    if len(msgs) >= 14:
        quiebres.append("conversacion_larga_sin_ot")

    if len(user_msgs) >= 6 and len(set(user_msgs)) <= 3:
        quiebres.append("loop_pocos_mensajes_distintos")

    for i in range(len(asst_msgs) - 1):
        if len(asst_msgs[i]) > 40 and similar(asst_msgs[i], asst_msgs[i + 1], 0.75):
            quiebres.append("loop_respuesta_bot_similar")
            break

    return list(dict.fromkeys(quiebres))


def extraer_keywords(blob: str) -> list[str]:
    b = blob.lower()
    found = []
    for kw in KEYWORDS:
        if kw == "cas-" and "cas-" in b:
            found.append(kw)
        elif kw != "cas-" and re.search(rf"\b{re.escape(kw)}", b):
            found.append(kw)
    return found


def ultimo_mensaje_asistente(conversacion: list[dict[str, Any]]) -> str:
    for m in reversed(conversacion):
        if m.get("role") == "assistant":
            return (m.get("content") or "").strip()
    return ""


def primera_hora(conversacion: list[dict[str, Any]], fecha_creacion: str | None) -> str:
    for m in conversacion:
        ts = m.get("timestamp") or ""
        if ts:
            try:
                dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                return dt.strftime("%H:%M")
            except ValueError:
                pass
    if fecha_creacion:
        try:
            if hasattr(fecha_creacion, "strftime"):
                return fecha_creacion.strftime("%H:%M")
            dt = datetime.fromisoformat(str(fecha_creacion).replace("Z", "+00:00"))
            return dt.strftime("%H:%M")
        except (ValueError, TypeError):
            pass
    return ""


def es_conversacion_corta(
    conversacion: list[dict[str, Any]],
    tipo_sesion: str | None,
) -> bool:
    n_msgs = len(conversacion)
    n_user = sum(1 for m in conversacion if m.get("role") == "user")
    if tipo_sesion and str(tipo_sesion).strip().lower() == "abandono":
        return True
    return n_msgs <= 2 or n_user <= 1


def es_error_tecnico_corto(user_text: str, asst_text: str) -> bool:
    if not user_text.strip() and not asst_text.strip():
        return True
    return any(re.search(p, asst_text) for p in ERROR_BOT_PATTERNS)


def clasificar_corta(user_text: str, asst_text: str) -> tuple[str, float]:
    """Clasificación por intención cuando la sesión no se desarrolló (≤2 turnos)."""
    if es_error_tecnico_corto(user_text, asst_text):
        return "Error", 0.18

    if any(re.search(p, user_text) for p in FRUSTRACION):
        return "Frustración", 0.35
    if any(re.search(p, user_text) for p in CONFUSION_PATTERNS):
        return "Confusión", 0.28
    if (
        any(re.search(p, user_text) for p in URGENCY_PATTERNS)
        or "reclamo" in user_text
        or "incumplimiento" in user_text
    ):
        return "Urgencia", 0.30
    if any(re.search(p, user_text) for p in SATISFACTION_PATTERNS):
        return "Satisfacción", 0.30
    if "estado de mi env" in user_text or any(m in asst_text for m in BOT_PIDE_OT):
        return "Resolución", 0.25
    if re.search(r"necesito ayuda|men[uú] principal|\bhola\b", user_text):
        return "Abandono", 0.24
    if re.search(r"informaci[oó]n sobre|productos|servicios", user_text):
        return "Resolución", 0.22
    return "Abandono", 0.22


def clasificar_sentimiento(
    conversacion: list[dict[str, Any]],
    cache: dict[str, dict[str, Any]] | None,
    conv_id: str,
    tipo_sesion: str | None = None,
) -> tuple[str, float]:
    if cache and conv_id in cache:
        c = cache[conv_id]
        return c["sentiment"], float(c.get("confidence", 0.5))

    user_text = " ".join(
        norm(m.get("content", "")) for m in conversacion if m.get("role") == "user"
    )
    asst_text = " ".join(
        norm(m.get("content", "")) for m in conversacion if m.get("role") == "assistant"
    )
    blob = f"{user_text} {asst_text}"
    quiebres = detectar_quiebres(conversacion)
    n_msgs = len(conversacion)

    if es_conversacion_corta(conversacion, tipo_sesion):
        return clasificar_corta(user_text, asst_text)

    score: dict[str, float] = {
        "Frustración": 0.0,
        "Confusión": 0.0,
        "Urgencia": 0.0,
        "Satisfacción": 0.0,
        "Resolución": 0.2,
    }

    if any(re.search(p, user_text) for p in FRUSTRACION):
        score["Frustración"] += 0.45
    if "senal_frustracion_cliente" in quiebres:
        score["Frustración"] += 0.35
    if "loop_mensaje_usuario_repetido" in quiebres or "iteracion_consulta_tracking" in quiebres:
        score["Frustración"] += 0.2
        score["Urgencia"] += 0.15

    if any(re.search(p, user_text) for p in CONFUSION_PATTERNS):
        score["Confusión"] += 0.4
    if user_text.count("?") >= 3:
        score["Confusión"] += 0.25

    if any(re.search(p, blob) for p in URGENCY_PATTERNS):
        score["Urgencia"] += 0.35
    if "reclamo" in blob and "estado de mi env" in user_text:
        score["Urgencia"] += 0.2

    if any(re.search(p, user_text) for p in SATISFACTION_PATTERNS):
        score["Satisfacción"] += 0.35
    if "caso creado" in asst_text or "cas-" in asst_text:
        score["Satisfacción"] += 0.35
    if "cas-" in blob and n_msgs >= 10:
        score["Satisfacción"] += 0.15

    if n_msgs <= 8 and "estado de mi env" in user_text and score["Frustración"] < 0.3:
        score["Resolución"] += 0.35

    sentiment = max(score, key=score.get)
    confidence = round(min(0.95, max(0.08, score[sentiment])), 2)
    return sentiment, confidence


def fila_a_dashboard(row: Any, cache: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    conv_id = str(row.get("session_id") or row.get("id") or "")
    conversacion = normalizar_conversacion(history_a_lista(row.get("history")))
    blob = " ".join(m.get("content", "") or "" for m in conversacion)
    keywords = extraer_keywords(blob)
    summary_raw = ultimo_mensaje_asistente(conversacion) or (
        conversacion[0].get("content", "") if conversacion else ""
    )
    summary = summary_raw.replace("\n", " ").strip()
    if len(summary) > 60:
        summary = summary[:57] + "..."

    sentiment, confidence = clasificar_sentimiento(
        conversacion,
        cache,
        conv_id,
        tipo_sesion=row.get("tipo_sesion"),
    )

    fecha_inicio = row.get("fecha_inicio") or row.get("fecha")
    if hasattr(fecha_inicio, "strftime"):
        fecha = fecha_inicio.strftime("%Y-%m-%d")
    elif fecha_inicio:
        fecha = str(fecha_inicio)[:10]
    else:
        fecha = "—"

    return {
        "id": conv_id,
        "sentiment": sentiment,
        "confidence": confidence,
        "messages": int(row.get("cantidad_mensajes") or len(conversacion)),
        "summary": summary,
        "date": fecha,
        "time": primera_hora(conversacion, fecha_inicio),
        "keywords": keywords,
        "conversation": conversacion,
    }


def pdf_a_dashboard(pdf, cache: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [fila_a_dashboard(row.to_dict(), cache) for _, row in pdf.iterrows()]


def _bloque_isn_vacio() -> dict[str, Any]:
    return {
        "por_dia": [],
        "total": {
            "total_respuestas": 0,
            "satisfecho_6_7": 0,
            "neutro_5": 0,
            "insatisfecho_1_4": 0,
            "isn_pct": None,
        },
    }


ISN_SQL = """
WITH base AS (
    SELECT
        Fecha,
        TRY_CAST(EvalIA AS INT) AS eval_ia
    FROM adl_gold.enol_v2.t_captura_api_onemarketer_encuesta_data_cruda
    WHERE Fecha >= '{fecha_desde}'
      AND Fecha <= '{fecha_hasta}'
      AND AtencionIA = 'Si'
      AND OperadorAbre = 'robot'
      AND OperadorCierra = 'robot'
      AND EvalIA IS NOT NULL
      AND TRIM(EvalIA) <> ''
)
SELECT
    Fecha AS fecha,
    COUNT(*) AS total_respuestas,
    SUM(CASE WHEN eval_ia IN (6,7) THEN 1 ELSE 0 END) AS satisfecho_6_7,
    SUM(CASE WHEN eval_ia BETWEEN 1 AND 4 THEN 1 ELSE 0 END) AS insatisfecho_1_4,
    SUM(CASE WHEN eval_ia = 5 THEN 1 ELSE 0 END) AS neutro_5,
    ROUND(
        (
            SUM(CASE WHEN eval_ia IN (6,7) THEN 1 ELSE 0 END)
            - SUM(CASE WHEN eval_ia BETWEEN 1 AND 4 THEN 1 ELSE 0 END)
        ) * 100.0 / COUNT(*),
        2
    ) AS isn_pct
FROM base
WHERE eval_ia BETWEEN 1 AND 7
GROUP BY Fecha
ORDER BY Fecha
"""


def _isn_comparativa_desde_filas(df) -> dict[str, Any]:
    por_dia = []
    tot_sat = tot_ins = tot_neu = tot_n = 0
    for _, r in df.iterrows():
        por_dia.append(
            {
                "fecha": str(r["fecha"]),
                "total_respuestas": int(r["total_respuestas"]),
                "satisfecho_6_7": int(r["satisfecho_6_7"]),
                "insatisfecho_1_4": int(r["insatisfecho_1_4"]),
                "neutro_5": int(r["neutro_5"]),
                "isn_pct": float(r["isn_pct"]) if r["isn_pct"] is not None else None,
            }
        )
        tot_sat += int(r["satisfecho_6_7"])
        tot_ins += int(r["insatisfecho_1_4"])
        tot_neu += int(r["neutro_5"])
        tot_n += int(r["total_respuestas"])

    isn_total = round((tot_sat - tot_ins) * 100.0 / tot_n, 2) if tot_n > 0 else None
    total = {
        "total_respuestas": tot_n,
        "satisfecho_6_7": tot_sat,
        "neutro_5": tot_neu,
        "insatisfecho_1_4": tot_ins,
        "isn_pct": isn_total,
    }
    return {
        "disponible": tot_n > 0,
        "fuente_principal": "databricks",
        "isn_global": {"por_dia": por_dia, "total": total},
        "solo_mongo": _bloque_isn_vacio(),
        "solo_databricks": _bloque_isn_vacio(),
        "nota": "ISN desde adl_gold.enol_v2.t_captura_api_onemarketer_encuesta_data_cruda (AtencionIA=Si, robot).",
    }


def isn_diario_desde_spark(spark, fecha_desde: str, fecha_hasta: str) -> dict[str, Any]:
    """ISN diario desde tabla gold (Spark en Databricks)."""
    sql = ISN_SQL.format(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    return _isn_comparativa_desde_filas(spark.sql(sql).toPandas())


def isn_diario_desde_sql(fecha_desde: str, fecha_hasta: str) -> dict[str, Any]:
    """ISN diario vía cluster Databricks (.env + DatabricksRestClient)."""
    from src.extract.databricks_client import DatabricksRestClient

    sql = ISN_SQL.format(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    client = DatabricksRestClient()
    try:
        import pandas as pd

        df = pd.DataFrame(client.fetch_data(sql))
        return _isn_comparativa_desde_filas(df)
    finally:
        client.close()


_RE_FILTRO_FECHAS = re.compile(
    r'<div class="filter-row">\s*'
    r'(?:(?!</div>\s*<div class="filter-row">).)*?'
    r'id="dateFrom"[^>]*>.*?'
    r'id="dateTo"[^>]*>.*?'
    r'id="btnResetDates"[^>]*>.*?</button>\s*'
    r'</div>\s*'
    r'<p id="dateRangeHint"></p>',
    re.S,
)


def _mover_filtro_fechas_al_inicio(html: str) -> str:
    """Desde/Hasta arriba del reporte; quita duplicados y tarjetas vacías."""
    html = re.sub(
        r'<div class="card filters[^"]*"[^>]*>\s*'
        r'<h3[^>]*>[^<]*Per[ií]odo[^<]*</h3>\s*</div>\s*',
        "",
        html,
        flags=re.S | re.I,
    )

    matches = list(_RE_FILTRO_FECHAS.finditer(html))
    if not matches:
        return html

    grid_pos = html.find('<div class="grid">')
    if len(matches) == 1 and grid_pos != -1 and matches[0].start() < grid_pos:
        return html

    bloque = matches[0].group(0)
    for m in reversed(matches):
        html = html[: m.start()] + html[m.end() :]

    tarjeta = (
        '        <div class="card filters filters-top" style="margin-bottom: 20px;">\n'
        '            <h3 style="margin-bottom: 12px; font-size: 16px;">📅 Período de análisis</h3>\n'
        f"            {bloque.strip()}\n"
        "        </div>\n\n"
    )
    if 'filters-top' not in html.split("</header>", 1)[-1].split('<div class="grid">', 1)[0]:
        html = html.replace("</header>", "</header>\n" + tarjeta, 1)
    return html


def _inyectar_config_html(
    html: str,
    *,
    desde: str,
    hasta: str,
    isn_comparativa: dict[str, Any],
) -> str:
    isn_json = json.dumps(isn_comparativa, ensure_ascii=False, default=str)
    bloque = (
        "<script>\n"
        f"window.EMILIA_DESDE = {json.dumps(desde)};\n"
        f"window.EMILIA_HASTA = {json.dumps(hasta)};\n"
        f"window.EMILIA_ISN_COMPARATIVA = {isn_json};\n"
        "</script>\n"
    )
    if "</body>" in html:
        return html.replace("</body>", bloque + "</body>", 1)
    return html + bloque


def generar_html(
    pdf,
    template_path: Path,
    salida_path: Path | None = None,
    *,
    spark=None,
    isn_comparativa: dict[str, Any] | None = None,
    titulo_periodo: str = "Emilia AKS · Conversaciones Mongo + ISN Databricks",
    sin_isn: bool = False,
) -> tuple[str, int, str, str]:
    """
    Genera HTML del dashboard de sentimientos.
    Returns: (html, n_conversaciones, fecha_desde, fecha_hasta)
    """
    all_data = pdf_a_dashboard(pdf)
    fechas = sorted({r["date"] for r in all_data if r.get("date") and r["date"] != "—"})
    desde = fechas[0] if fechas else ""
    hasta = fechas[-1] if fechas else ""

    template = template_path.read_text(encoding="utf-8")
    if titulo_periodo:
        template = re.sub(
            r'<p class="subtitle">.*?</p>',
            f'<p class="subtitle">{titulo_periodo}</p>',
            template,
            count=1,
        )

    data_json = json.dumps(all_data, ensure_ascii=False, default=str)
    html = template
    for patron in (
        r"let allData = \[\];",
        r"const allData = \[\];",
        r"let allData = \[.*?\];",
        r"const allData = \[.*?\];",
    ):
        html, n = re.subn(patron, f"let allData = {data_json};", html, count=1, flags=re.S)
        if n:
            break
    else:
        raise ValueError("No se encontró 'allData = []' en la plantilla HTML.")

    if not sin_isn and desde and hasta:
        isn_cmp = isn_comparativa
        if isn_cmp is None and spark is not None:
            isn_cmp = isn_diario_desde_spark(spark, desde, hasta)
        if isn_cmp is not None:
            html = _inyectar_config_html(html, desde=desde, hasta=hasta, isn_comparativa=isn_cmp)

    html = _mover_filtro_fechas_al_inicio(html)

    if salida_path:
        salida_path.parent.mkdir(parents=True, exist_ok=True)
        salida_path.write_text(html, encoding="utf-8")

    return html, len(all_data), desde, hasta
