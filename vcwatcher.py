import os
import time
import threading

from dotenv import load_dotenv
from watchdog.observers import Observer

from handlers.file_event_handler import FileEventHandler
from handlers.file_history_handler import FileHistoryHandler
from handlers.completion_handler import CompletionHandler

from utils.utils import Utils

class VCWatcher:
    def __init__(self, API_KEY: str):
        load_dotenv()

        self.api_key = os.getenv(API_KEY)

        if not self.api_key:
            raise ValueError(f"API key not found in .env file: {API_KEY}")

        self.utils = Utils()
        self.completion = CompletionHandler(self.api_key)
        self.file_history = FileHistoryHandler(utils=self.utils)

        self.event_handler = FileEventHandler(
            history_handler=self.file_history,
            completion_handler=self.completion,
            utils=self.utils
        )

        self.path = '.'

    def log_api_key(self) -> str:
       return self.api_key
    
    def observe_dir(self) -> None:
        observer = Observer()
        observer.schedule(self.event_handler, self.path, recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def start_observing_in_thread(self) -> None:
        observing_thread = threading.Thread(target=self.observe_dir)
        observing_thread.daemon = True
        observing_thread.start()

    def run(self) -> None:
        self.file_history.construct_tree()
        self.start_observing_in_thread()

        while True:
            print("\nEnter 'commit-generate' to collect diffs and generate a message.\n")
            print("Enter 'exit' or 'quit' to close VCWatcher.")
            command = input().lower()
            if command == "commit-generate":
                response = watch.completion.generate_commit_msg(
                    watch.completion.commit_cache
                )
                print(response)
            elif command in ("exit", "quit"):
                break
            else:
                print("Unknown command...")


if __name__ == "__main__":
    watch = VCWatcher("API_KEY")
    watch.run()
