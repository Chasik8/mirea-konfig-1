import unittest
from unittest import mock
from unittest.mock import patch
from io import StringIO
from main1 import ShellEmulator
class TestShellEmulator(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_ls(self, mock_stdout):
        emulator = ShellEmulator('config.csv')
        emulator.fs = mock.Mock()
        emulator.fs.namelist.return_value = ['/file1', '/file2']
        emulator.execute_command('ls')
        output = mock_stdout.getvalue()
        self.assertIn('/file1', output)
        self.assertIn('/file2', output)

if __name__ == '__main__':
    unittest.main()
