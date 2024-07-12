import os
import time
from dotenv import load_dotenv

from watchdog.observers import Observer

from file_event_handler import FileEventHandler
from file_history_handler import FileHistoryHandler

from utils import Utils

class VCWatcher:
    load_dotenv()

    def __init__(self, API_KEY: str):
        self.api_key = os.getenv(API_KEY)
        self.utils = Utils()
        self.event_handler = FileEventHandler(self.utils)
        self.file_history = FileHistoryHandler(utils=self.utils)

        self.path = '.'

    def log_api_key(self):
       return self.api_key
    
    def event_logger(self):
        observer = Observer()
        observer.schedule(self.event_handler, self.path, recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

watch = VCWatcher("API_KEY")
watch.file_history.construct_tree()
watch.file_history.show_directory_tree()
watch.event_logger()