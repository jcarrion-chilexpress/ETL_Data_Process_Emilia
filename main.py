## main.py
## main.py
import sys
from src.flow.flow import (step_get_sqlquery
                           ,step_generar_pdf
                           ,step_save_table
                           ,step_create_BD_reclamos)
from config.config import get_settings


def main():
    settings = get_settings()
    # step_create_BD_reclamos(spark)

    # file_name = ["emilia_dashboard_base"
    #              ,"sentimientos_emilia_dashboard"]
    # for file in file_name:
    #     success,tabla_sql,query = step_get_sqlquery(file)
    #     if success:
    #         success, pdf = step_generar_pdf(query, file, file_save=False)
        
            # if success:
            #     step_save_table(spark, pdf, tabla_sql)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
