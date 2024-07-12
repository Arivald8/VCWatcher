import unittest
from vcwatcher import VCWatcher

class TestVCWatcher(unittest.TestCase):
    def setUp(self) -> None:
        self.test_watch = VCWatcher("TEST_API_KEY")
        return super().setUp()
    
    def test_load_api_key(self):
        self.assertEqual(self.test_watch.log_api_key(), "sk-proj-mdHL3BlbkFJWcGcDD4noiLp9H1ZQJDP72m")

    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()