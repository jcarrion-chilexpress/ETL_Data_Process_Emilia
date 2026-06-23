import sys
from src.utils.utils import leer_parquet
from src.load.export_sentimientos_pbi import orquestador

def main():
    orquestador()
    # archivo = "sentimientos_pbi.parquet"
    # parquet_file =leer_parquet(archivo)
    # print(parquet_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
