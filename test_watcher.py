import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import shutil
import time

from watchdog.events import FileSystemEvent

from vcwatcher import VCWatcher

from handlers.file_history_handler import FileHistoryHandler
from handlers.file_event_handler import FileEventHandler
from handlers.completion_handler import CompletionHandler

from utils.utils import Utils
from utils.file_repr import FileReprEncoder


class TestVCWatcher(unittest.TestCase):
    """
    Arguments starting with a single underscore are intentional and
    required by the `@patch` decorators, even if they are no used directly. 
    """
    
    @patch('vcwatcher.load_dotenv')
    @patch('vcwatcher.os.getenv')
    @patch('vcwatcher.Utils')
    @patch('vcwatcher.CompletionHandler')
    @patch('vcwatcher.FileHistoryHandler')
    @patch('vcwatcher.FileEventHandler')
    def setUp(
        self, 
        _mock_file_event_handler, 
        _mock_file_history_handler, 
        _mock_completion_handler, 
        _mock_utils, 
        _mock_load_dotenv,
        mock_getenv,
        ):

        mock_getenv.return_value = 'dummy_api_key'
        self.vcwatcher = VCWatcher('dummy_api_key')

    @patch('vcwatcher.os.getenv')
    def test_init_raises_value_error_if_api_key_not_found(self, mock_getenv):
        mock_getenv.return_value = None
        with self.assertRaises(ValueError):
            VCWatcher('API_KEY')

    @patch('vcwatcher.Observer')
    @patch('vcwatcher.time.sleep', side_effect=KeyboardInterrupt)
    def test_observe_dir_starts_observer(self, mock_sleep, mock_observer):
        mock_observer_instance = mock_observer.return_value
        self.vcwatcher.observe_dir()
        mock_observer_instance.schedule.assert_called_once()
        mock_observer_instance.start.assert_called_once()
        mock_observer_instance.stop.assert_called_once()
        mock_observer_instance.join.assert_called_once()

    @patch('vcwatcher.threading.Thread')
    def test_start_observing_in_thread_starts_thread(self, mock_thread):
        self.vcwatcher.start_observing_in_thread()
        mock_thread.assert_called_once_with(target=self.vcwatcher.observe_dir)
        mock_thread_instance = mock_thread.return_value
        mock_thread_instance.daemon = True
        mock_thread_instance.start.assert_called_once()

    @patch('vcwatcher.sys.argv', ['vcwatcher.py', '/some/directory'])
    @patch('vcwatcher.Path')
    @patch('vcwatcher.input', side_effect=['exit'])
    @patch.object(VCWatcher, 'start_observing_in_thread')
    def test_run(self, mock_start_observing_in_thread, mock_input, mock_path):
        mock_path_instance = mock_path.return_value
        mock_path_instance.is_dir.return_value = True
        self.vcwatcher.run()
        mock_path.assert_called_once_with('/some/directory')
        mock_path_instance.is_dir.assert_called_once()
        self.assertEqual(self.vcwatcher.path, mock_path_instance)
        self.vcwatcher.file_history.construct_tree.assert_called_once()
        mock_start_observing_in_thread.assert_called_once()

    @patch('vcwatcher.sys.argv', ['vcwatcher.py'])
    @patch('vcwatcher.print')
    def test_run_with_incorrect_arguments(self, mock_print):
        self.vcwatcher.run()
        mock_print.assert_called_once_with("Usage: `python vcwatcher.py <directory_to_monitor>`")

    @patch('vcwatcher.sys.argv', ['vcwatcher.py', '/invalid/directory'])
    @patch('vcwatcher.Path')
    @patch('vcwatcher.print')
    def test_run_with_invalid_directory(self, mock_print, mock_path):
        mock_path_instance = mock_path.return_value
        mock_path_instance.is_dir.return_value = False
        self.vcwatcher.run()
        mock_path.assert_called_once_with('/invalid/directory')
        mock_path_instance.is_dir.assert_called_once()
        mock_print.assert_called_once_with(f"Error: {mock_path_instance} is not a valid directory.")


class TestFileHistoryHandler(unittest.TestCase):
    def setUp(self):
        # Temporary test directory will be created on setUp and removed on tearDown:
        # "{'test_file.txt': FileRepr Object @ test_temp_dir/test_file.txt}"
        self.mock_utils = MagicMock(Utils)
        self.mock_utils.excluded_dirs = {
            'node_modules', 
            '.git', 
            '__pycache__', 
            'venv'
        }
        self.mock_utils.excluded_files = {
            'db.sqlite3', 
            '.gitignore', 
            'package-lock.json', 
            '.env',
        }
        self.file_history_handler = FileHistoryHandler(utils=self.mock_utils)
        self.test_dir = Path('test_temp_dir')
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.test_file = self.test_dir / 'test_file.txt'
        self.test_file.write_text('Tester')

    def tearDown(self) -> None:
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        return super().tearDown()

    def test_init(self):
        self.assertIsInstance(self.file_history_handler.utils, Utils)
        self.assertEqual(self.file_history_handler.root_path, Path('.'))
        self.assertEqual(self.file_history_handler.tree, {})
        self.assertEqual(self.file_history_handler.visited, set())

    def test_get_directory_tree(self):
        directory_tree = str(self.file_history_handler.get_directory_tree(self.test_dir))
        self.assertEqual(directory_tree, "{'test_file.txt': FileRepr Object @ test_temp_dir/test_file.txt}")

    def test_construct_tree(self):
        self.file_history_handler.visited.add(Path('some/dir'))
        with patch.object(self.file_history_handler, 'get_directory_tree', return_value={'mock_tree': {}}):
            self.file_history_handler.construct_tree()
        self.assertEqual(self.file_history_handler.tree, {'.': {'mock_tree': {}}})
        self.assertEqual(self.file_history_handler.visited, set())

    @patch('json.dumps')
    def test_show_directory_tree(self, mock_json_dumps):
        self.file_history_handler.tree = {'mock_tree': {}}
        self.file_history_handler.show_directory_tree()
        mock_json_dumps.assert_called_once_with(self.file_history_handler.tree, cls=FileReprEncoder, indent=4)


    def test_get_file_repr_excluded(self):
        self.file_history_handler.tree = {
            '.': {
                'file1.txt': 'file1_repr',
                'dir1': {
                    'file2.txt': 'file2_repr'
                }
            }
        }
        self.mock_utils.excluded_files = ['file2.txt']
        self.mock_utils.modified_file_path = '.\\dir1\\file2.txt'
        file_repr = self.file_history_handler.get_file_repr()
        self.assertEqual(file_repr, "Warning: '.\\dir1\\file2.txt' found in excluded.")

    def test_compare_files(self):
        old_file = "line1\nline2\nline3"
        new_file = "line1\nline3\nline4"
        differences = self.file_history_handler.compare_files(old_file, new_file)
        expected_differences = ['- line2', '+ line4']
        self.assertEqual(differences, expected_differences) 


class TestFileEventHandler(unittest.TestCase):
    def setUp(self):
        self.mock_history_handler = MagicMock(spec=FileHistoryHandler)
        self.mock_completion_handler = MagicMock(spec=CompletionHandler)
        self.mock_utils = MagicMock(spec=Utils)
        self.file_event_handler = FileEventHandler(
            self.mock_history_handler,
            self.mock_completion_handler,
            self.mock_utils
        )

    @patch('time.time', return_value=100.0)
    def test_on_modified_ignored_due_to_debouce(self, mock_time):
        self.mock_utils.last_modified_time = 99.5
        self.mock_utils.debounce_time = 1.0
        event = MagicMock(spec=FileSystemEvent)
        event.is_directory = False
        event.src_path = "test.txt"

        self.file_event_handler.on_modified(event)

        self.assertEqual(self.mock_utils.last_modified_time, 99.5)
        self.assertFalse(self.mock_history_handler.get_file_repr.called)

    @patch('time.time', return_value=100.0)
    def test_on_modified_processes_event(self, mock_time):
        self.mock_utils.last_modified_time = 98.0
        self.mock_utils.debounce_time = 1.0
        event = MagicMock(spec=FileSystemEvent)
        event.is_directory = False
        event.src_path = "test.txt"

        old_file_repr = MagicMock()
        new_file_repr = MagicMock()
        
        self.mock_history_handler.get_file_repr.side_effect = [old_file_repr, new_file_repr]

        diffs = ['diff1', 'diff2']

        self.mock_history_handler.compare_files.return_value = diffs

        self.file_event_handler.on_modified(event)

        self.assertEqual(self.mock_utils.last_modified_time, 100.0)
        self.assertEqual(self.mock_utils.modified_file_path, "test.txt")
        self.mock_history_handler.construct_tree.assert_called_once()
        self.mock_history_handler.compare_files.assert_called_once_with(
            old_file_repr.file_content, new_file_repr.file_content
        )
        self.mock_completion_handler.store_commit.assert_called_once_with(
            "test.txt", diffs
        )

    @patch('time.time', return_value=100.0)
    def test_on_modified_handles_attribute_error(self, mock_time):
        self.mock_utils.last_modified_time = 98.0
        self.mock_utils.debounce_time = 1.0
        event = MagicMock(spec=FileSystemEvent)
        event.is_directory = False
        event.src_path = "test.txt"

        old_file_repr = MagicMock()
        new_file_repr = MagicMock()
        self.mock_history_handler.get_file_repr.side_effect = [old_file_repr, new_file_repr]
        self.mock_history_handler.compare_files.side_effect = AttributeError("mocked error")

        with self.assertLogs(level='ERROR') as log:
            self.file_event_handler.on_modified(event)

        self.assertIn("Error comparing files: mocked error", log.output[0])

if __name__ == '__main__':
    unittest.main()
