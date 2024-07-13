import os
import time
import threading
from dotenv import load_dotenv
from watchdog.observers import Observer

from file_event_handler import FileEventHandler
from file_history_handler import FileHistoryHandler
from completion_handler import CompletionHandler

from utils import Utils

class VCWatcher:
    load_dotenv()

    def __init__(self, API_KEY: str):
        self.api_key = os.getenv(API_KEY)

        self.utils = Utils()

        self.completion = CompletionHandler(self.api_key)

        self.file_history = FileHistoryHandler(utils=self.utils)

        self.event_handler = FileEventHandler(
            history_handler=self.file_history,
            completion_handler=self.completion,
            utils=self.utils
        )

        self.path = '.'

    def log_api_key(self):
       return self.api_key
    
    def observe_dir(self):
        observer = Observer()
        observer.schedule(self.event_handler, self.path, recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    def start_observing_in_thread(self):
        observing_thread = threading.Thread(target=self.observe_dir)
        observing_thread.daemon = True
        observing_thread.start()


if __name__ == "__main__":
    watch = VCWatcher("API_KEY")
    # Construct Tree
    watch.file_history.construct_tree()
    # Watch for changes
    watch.start_observing_in_thread()

    while True:
        print("\nEnter 'commit-generate' to collect diffs and generate a message.\n")
        print("Enter 'exit' or 'quit' to close VCWatcher.")
        command = input()
        if command == "commit-generate":
            watch.completion.generate_commit_msg(
                watch.completion.commit_cache
            )
        elif command == "exit" or command == "quit":
            exit()
        else:
            print("Unknown command...")


# Start
# Construct Tree
# Watch for changes... 
# Change detected
# Store file name, file path
# Perform lookup on tree given file path
# Build context with file content + detected changes