## main.py
import sys
from src.infra.spark import get_spark
from src.flow.flow import step_procesar_tabla
from pyspark.sql import SparkSession
from src.load.load_data_emilia import cargar_datos_dashboard_base
from src.catalog.catalog_manager import get_catalogo_manager

spark = get_spark()

def main():
    ## --------------------------------- ##
    catalog = get_catalogo_manager()
    tablename = "t_emilia_dashboard_base"

    table = catalog.obtener_tabla(
        tablename)

    cargar_datos_dashboard_base(
        spark=spark,
        table=table)

    # df_exploded = get_conversations_dataframe(
    #     spark=spark,
    #     fecha_desde="2026-07-01",
    # )
    # df_exploded.show(10)

    # ## --------------------------------------- ##
    # table = "t_emilia_dashboard_base"
    # step_procesar_tabla(spark
    #                     ,table_name=table)
    
    # table = "t_sentimientos_emilia"
    # step_procesar_tabla(spark
    #                     ,table_name=table)
    ## --------------------------------------- ##

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(40)


