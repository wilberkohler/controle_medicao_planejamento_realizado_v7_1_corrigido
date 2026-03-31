from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "controle_medicao.db"

APP_NAME = "Controle de Medição - Planejamento x Realizado"
APP_WIDTH = 1600
APP_HEIGHT = 950
