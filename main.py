## main.py
import pandas as pd
import sys
from src.flow.flow import (step_generar_pdf
                           ,step_save_table
                           ,step_create_BD_reclamos
                           ,step_generar_dfs_sql)
from src.utils.utils import (clear_terminal,get_fecha_carga)
from src.infra.spark import get_spark
from src.catalog.catalog_manager import get_catalogo_manager
from src.catalog.sql_manager import SQLManager
from src.catalog.table_manager import TableManager
from pyspark.sql.functions import lit
clear_terminal()

catalog = get_catalogo_manager()

def main():
    spark = get_spark()
    table = catalog.obtener_tabla(
        "t_emilia_dashboard_base"
    )

    sql = SQLManager.read(
        table.query_sql_path,
        dias=table.where
    )

    dfs = spark.sql(sql)
    dfs = dfs.withColumn('fecha_carga'
                            ,get_fecha_carga())

    TableManager(spark).save(
        dfs,
        table
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(40)

