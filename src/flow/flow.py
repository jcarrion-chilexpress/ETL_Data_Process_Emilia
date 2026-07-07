## src/flow/flow.py
## main.py
import sys
from src.utils.utils import (clear_terminal)
from src.infra.spark import get_spark
from src.catalog.catalog_manager import get_catalogo_manager
from src.catalog.table_manager import TableManager
from src.catalog.dataframe_manager import DataFrameManager
clear_terminal()

def step_procesar_tabla(spark,table_name):
    catalog = get_catalogo_manager()
    df_manager = DataFrameManager(spark)
    ## --------------------------------- ##
    table = catalog.obtener_tabla(
        table_name
        )

    dfs = df_manager.build(table)
    ## --------------------------------- ##
    TableManager(spark).save(
                            dfs,
                            table)
    ## --------------------------------- ##


# def step_create_BD_reclamos(spark,load_table:bool = False):
#     logger.info(f'Creando tabla de reclamos')
#     success,archivos = crear_resumen_reclamos()
#     path_reclamos = settings.reclamos_path

#     try:
#         if success:
#             for archivo in archivos:
#                 parquet = read_parquet(archivo,path_reclamos)
#                 nombre_tabla = 'reclamos_'+archivo

#                 if load_table:
#                     step_save_table(spark,parquet,nombre_tabla)
#     except Exception as e:
#         logger.exception(f'Error Creando tabla de reclamos !: {e}')

