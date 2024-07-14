import unittest
from unittest.mock import patch
from vcwatcher import VCWatcher

class TestVCWatcher(unittest.TestCase):
    @patch('vcwatcher.load_dotenv')
    @patch('vcwatcher.os.getenv')
    @patch('vcwatcher.Utils')
    @patch('vcwatcher.CompletionHandler')
    @patch('vcwatcher.FileHistoryHandler')
    @patch('vcwatcher.FileEventHandler')
    def setUp(self, mock_file_event_handler, mock_file_history_handler, mock_completion_handler, mock_utils, mock_getenv, mock_load_dotenv):
        mock_getenv.return_value = 'dummy_api_key'
        self.vcwatcher = VCWatcher('API_KEY')

    def test_init_loads_api_key(self):
        self.assertEqual(self.vcwatcher.api_key, 'dummy_api_key')

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

if __name__ == '__main__':
    unittest.main()
