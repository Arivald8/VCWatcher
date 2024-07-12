class Utils:
    def __init__(self):
        self.debounce_time: int = 1  # Debounce time in seconds
        self.last_modified_time: int = 0

        self.modified_file_path = ""

        self.excluded_dirs = {
            'node_modules', 
            '.git', 
            '__pycache__', 
            'venv'
        }
        self.excluded_files = {
            'db.sqlite3', 
            '.gitignore', 
            'package-lock.json', 
            '.env',
        }
