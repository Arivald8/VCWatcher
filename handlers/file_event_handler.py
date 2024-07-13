import time
from typing import Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler

# For typing only -->
from .completion_handler import CompletionHandler
from .file_history_handler import FileHistoryHandler
from utils.utils import Utils
# For typing only -->

class FileEventHandler(FileSystemEventHandler):
    def __init__(
            self, 
            history_handler: FileHistoryHandler,
            completion_handler: CompletionHandler,
            utils: Utils
        ) -> None:

        super().__init__()

        self.history_handler = history_handler
        self.completion_handler = completion_handler
        self.utils = utils

        
    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
    
            current_time = time.time()
            if current_time - self.utils.last_modified_time < self.utils.debounce_time:
                return
            
            self.utils.last_modified_time = current_time
            self.utils.modified_file_path = event.src_path

            # Store file content before changes
            old = self.history_handler.get_file_repr()

            # Reconstruct tree with new changes
            self.history_handler.construct_tree()

            # Store file content after changes
            new = self.history_handler.get_file_repr()

            # Collect diffs and store in memory
            try:
                diffs = self.history_handler.compare_files(old.file_content, new.file_content)
                self.completion_handler.store_commit(self.utils.modified_file_path, diffs)
            except AttributeError as e:
                print(f"Error comparing files: {e}")     

            return super().on_modified(event)
      

    


