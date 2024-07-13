import time

from watchdog.events import FileSystemEvent, FileSystemEventHandler

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, history_handler, completion_handler, utils) -> None:
        self.history_handler = history_handler
        self.completion_handler = completion_handler
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

            # Store file content before changes
            old = self.history_handler.get_file_repr()

            # Reconstruct tree with new changes
            self.history_handler.construct_tree()

            # Store file content after changes
            new = self.history_handler.get_file_repr()

            print("DEBUGGER")

            try:
                diffs = self.history_handler.compare_files(old.file_content, new.file_content)
                commit_message = self.completion_handler.generate_commit_msg(diff_state=diffs)
                print("Commit Message:")
                print(commit_message.message.content)

            except AttributeError:
                print("Warning: No operations allowed on excluded files and directories")
            
            print("ENDBUGGER")
            

        return super().on_modified(event)
    


