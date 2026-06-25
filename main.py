## main.py
import sys
import os
from src.flow.flow import (step_get_sqlquery
                           ,step_generar_pdf
                           ,step_create_table_Databricks)
from src.utils.utils import leer_parquet
from config.config import get_settings

os.system('cls')

def main():
    settings = get_settings()
    json_file = settings.config_path
    file_name = "sentimientos_emilia_dashboard" 
    #"emilia_dashboard_base"
    success,tabla_sql,query = step_get_sqlquery(file_name)

    if success:
        step_generar_pdf(query,file_name)
    
    df = leer_parquet(file_name+'.parquet')
    step_create_table_Databricks(df,tabla_sql)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

