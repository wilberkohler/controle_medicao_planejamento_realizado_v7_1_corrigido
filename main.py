from database.db import initialize_database
from ui.main_window import run_app

if __name__ == "__main__":
    initialize_database()
    run_app()
