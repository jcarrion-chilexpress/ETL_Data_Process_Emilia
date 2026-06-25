## main.py
import sys
import os
from src.flow.flow import (step_get_sqlquery
                           ,step_generar_pdf
                           ,step_save_table)
from config.config import get_settings

# from pyspark.sql import SparkSession
# spark = SparkSession.builder.getOrCreate()

os.system('cls')

def main():
    settings = get_settings()
    json_file = settings.config_path
    file_name = ["sentimientos_emilia_dashboard"
                ,"emilia_dashboard_base"]

    for file in file_name:
        success,tabla_sql,query = step_get_sqlquery(file)

        if success:
            success, pdf = step_generar_pdf(query, file)
        
            if success:
                step_save_table(spark, pdf, tabla_sql)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
