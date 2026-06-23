import sys
from src.load.export_sentimientos_pbi import orquestador

def main():
    orquestador()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

