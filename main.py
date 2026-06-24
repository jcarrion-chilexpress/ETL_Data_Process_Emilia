## main.ipynb
import sys
from src.load.export_sentimientos_pbi import (
    orquestador
)
from config.config import get_settings

def main():
    settings = get_settings()
    df = orquestador(
            desde="2026-06-01",
            hasta="2026-06-20"
            )
    print(df)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
