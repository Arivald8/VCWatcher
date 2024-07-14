import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os
import threading
from vcwatcher import VCWatcher

class TestVCWatcher(unittest.TestCase):
    """
    This test suite covers various aspects of the VCWatcher class:

    1. It tests the API key loading functionality.
    2. It checks if an exception is raised when an invalid API key is provided.
    3. It tests the observe_dir method using mocks.
    4. It verifies that start_observing_in_thread creates and starts a new thread.
    5. It tests the run method with both invalid and valid paths.
    6. It checks the 'commit-generate' functionality within the run method.

    Note that this test suite uses mocking extensively to avoid actual file 
    system operations and to control the behavior of external dependencies.
    """
    def setUp(self) -> None:
        # Create a mock .env file with a test API key
        with open('.env', 'w') as f:
            f.write('TEST_API_KEY=sk-test-api-key')
        self.test_watch = VCWatcher("TEST_API_KEY")
        return super().setUp()
    
    
    def tearDown(self) -> None:
        os.remove('.env')
        return super().tearDown()
    
    
    def test_load_api_key(self):
        self.assertEqual(self.test_watch.log_api_key(), "sk-test_api_key")


    def test_init_no_api_key(self):
        with self.assertRaises(ValueError):
            VCWatcher("NONEXISTENT_KEY")


    @patch('vcwatcher.Observer')
    def test_observe_dir(self, mock_observer):
        mock_observer_instance = MagicMock()
        mock_observer.return_value = mock_observer_instance

        self.test_watch.observe_dir()

        mock_observer_instance.schedule.assert_called_once()
        mock_observer_instance.start.assert_called_once()
        mock_observer_instance.join.assert_called_once()


    @patch('threading.Thread')
    def test_start_observing_in_thread(self, mock_thread):
        self.test_watch.start_observing_in_thread()

        mock_thread.assert_called_once_with(target=self.test_watch.observe_dir)
        mock_thread.return_value.start.assert_called_once()


    @patch('builtins.print')
    @patch('builtins.input')
    @patch('vcwatcher.VCWatcher.start_observing_in_thread')
    def test_run_invalid_path(self, mock_start_observing, mock_input, mock_print):
        with patch('sys.argv', ['vcwatcher.py', '/invalid/path']):
            self.test_watch.run()

        mock_print.assert_any_call("Error: /invalid/path is not a valid directory.")


    @patch('builtins.print')
    @patch('builtins.input')
    @patch('vcwatcher.VCWatcher.start_observing_in_thread')
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_run_valid_path(self, mock_is_dir, mock_start_observing, mock_input, mock_print):
        mock_input.side_effect = ['exit']
        with patch('sys.argv', ['vcwatcher.py', '/valid/path']):
            self.test_watch.run()
        
        mock_start_observing.assert_called_once()
        mock_print.assert_any_call("\nVCWatcher is observing /valid/path...")

    
    @patch('builtins.print')
    @patch('builtins.input')
    @patch('vcwatcher.VCWatcher.start_observing_in_thread')
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_run_commit_generate(self, mock_is_dir, mock_start_observing, mock_input, mock_print):
        mock_input.side_effect = ['commit-generate', 'exit']
        with patch('sys.argv', ['vcwatcher.py', '/valid/path']):
            with patch.object(self.test_watch.completion, 'generate_commit_msg', return_value='Mocked commit message'):
                self.test_watch.run()
        
        mock_print.assert_any_call('Mocked commit message')


if __name__ == '__main__':
    unittest.main()