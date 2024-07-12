import time

from watchdog.events import FileSystemEvent, FileSystemEventHandler

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, utils) -> None:
        self.utils = utils
        super().__init__()
        
    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            current_time = time.time()
            if current_time - self.utils.last_modified_time < self.utils.debounce_time:
                return
            self.utils.last_modified_time = current_time

            print("Changes detected.")
            self.utils.modified_file_path = event.src_path
            print("Modified file path:", self.utils.modified_file_path)

        return super().on_modified(event)
    


