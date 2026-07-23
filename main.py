## main.py
import sys
from src.infra.spark import get_spark
from src.flow.flow import step_procesar_tabla
from src.catalog.catalog_manager import get_catalogo_manager
from src.load.load_data_emilia import cargar_datos_dashboard_base
spark = get_spark()


def main():
    ## --------------------------------- ##
    # table = "t_emilia_dashboard_base"
    # catalog = get_catalogo_manager()
    # ## --------------------------------- ##
    # table = catalog.obtener_tabla(
    #     table_name
    #     )

    # cargar_datos_dashboard_base(spark
    #                             ,table=table)

    table = "t_emilia_dashboard_base"
    step_procesar_tabla(spark
                        ,table_name=table)

    # ## --------------------------------------- ##
    table = "t_sentimientos_emilia"
    step_procesar_tabla(spark
                        ,table_name=table)
    ## --------------------------------------- ##

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(40)

