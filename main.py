## main.py
import sys
import os
from src.flow.flow import (step_get_sqlquery
                           ,step_generar_pdf)
from src.load.save_delta import guardar_delta_merge
from src.utils.utils import leer_parquet
from config.config import get_settings

os.system('cls')

def main():
    settings = get_settings()
    json_file = settings.config_path
    file_name = "emilia_dashboard_base"
    success,query = step_get_sqlquery(file_name)

    if success:
        step_generar_pdf(query,file_name)
    
    df = leer_parquet(file_name+'.parquet')
    print(df)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

