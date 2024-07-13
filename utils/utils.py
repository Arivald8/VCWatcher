class Utils:
    content_prompt = """
            Generate professional version control commit message from provided list of diffs.
            + sign represents an addition of content, - sign represents removal. Be descriptive
            and verbose. Do not include each line in the message.
        """

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
