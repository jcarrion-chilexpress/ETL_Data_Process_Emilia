### export_sentimientos_pbi.py
"""
Exporta conversaciones clasificadas para Power BI.
  python export_sentimientos_pbi.py
  python export_sentimientos_pbi.py --desde 2025-01-01 --hasta 2025-06-15
  python export_sentimientos_pbi.py --datos data/emilia_dashboard_base.parquet
  python export_sentimientos_pbi.py --csv
"""
from __future__ import annotations
import argparse
import pandas as pd
from pathlib import Path
#####################################
from src.load.emilia_dashboard_sentimientos import pdf_a_dashboard
from config.config import get_settings

## ------------------------------- ##
SALIDA_DEFAULT= get_settings().salida_default
DATOS_DEFAULT =get_settings().datos_default
#####################################

def cargar_datos_archivo(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}")
    if ruta.suffix.lower() == ".parquet":
        return pd.read_parquet(ruta)
    if ruta.suffix.lower() == ".csv":
        return pd.read_csv(ruta)
    raise ValueError("Use .parquet o .csv")


def cargar_datos(
    desde: str | None,
    hasta: str | None,
    datos: Path | None,
) -> pd.DataFrame:
    if datos:
        return cargar_datos_archivo(datos)

    if DATOS_DEFAULT.exists():
        return cargar_datos_archivo(DATOS_DEFAULT)

    from src.extract.databricks_client import cargar_dashboard_base, configurado

    if not configurado():
        raise SystemExit(
            "Sin datos locales ni Databricks configurado.\n"
            "Usa --datos <parquet|csv> o configura .env (DATABRICKS_*)."
        )
    return cargar_dashboard_base(fecha_desde=desde, fecha_hasta=hasta)


def orquestador() -> None:
    parser = argparse.ArgumentParser(description="Export sentimientos para Power BI")
    parser.add_argument("--desde", help="Fecha desde YYYY-MM-DD (solo Databricks)")
    parser.add_argument("--hasta", help="Fecha hasta YYYY-MM-DD (solo Databricks)")
    parser.add_argument(
        "--datos",
        type=Path,
        help="Parquet/CSV local (default: data/emilia_dashboard_base.parquet si existe)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=SALIDA_DEFAULT,
        help=f"Salida parquet (default: {SALIDA_DEFAULT})",
    )
    parser.add_argument("--csv", action="store_true", help="Exportar también CSV")
    args = parser.parse_args()

    pdf = cargar_datos(args.desde, args.hasta, args.datos)
    if "history" not in pdf.columns:
        raise SystemExit("El dataset debe tener columna 'history'.")

    rows = pdf_a_dashboard(pdf)
    pbi = pd.DataFrame(
        [
            {
                "session_id": r["id"],
                "fecha": r["date"],
                "sentiment": r["sentiment"],
                "confidence": r["confidence"],
                "messages": r["messages"],
            }
            for r in rows
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pbi.to_parquet(args.output, index=False)
    print(f"OK: {len(pbi)} filas → {args.output}")

    if args.csv:
        csv_path = args.output.with_suffix(".csv")
        pbi.to_csv(csv_path, index=False)
        print(f"OK: CSV → {csv_path}")

    por_sentiment = pbi.groupby("sentiment", sort=False).size().sort_values(ascending=False)
    total = len(pbi)

    print("\nDistribución:")

    for sentiment, count in por_sentiment.items():
        pct = round(count / total * 100) if total else 0
        print(f"  {sentiment}: {count} ({pct}%)")

