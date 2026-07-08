## main.py
import sys
from src.infra.spark import get_spark
from src.flow.flow import step_procesar_tabla

def main():
    spark = get_spark()
    ## --------------------------------- ##
    table = "t_emilia_dashboard_base"
    step_procesar_tabla(spark
                        ,table_name=table)
    
    table = "t_sentimientos_emilia"
    step_procesar_tabla(spark
                        ,table_name=table)    
    ## --------------------------------- ##

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(40)

