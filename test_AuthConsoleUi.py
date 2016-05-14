import unittest
import sys
from mock import Mock
from StringIO import StringIO
from authentication import AuthConsoleUi

class TestAuthConsoleUi(unittest.TestCase):
    def test_can_open(self):
        subprocess = Mock()
        stdin = StringIO('a code')
        stdout = StringIO()
        stderr = StringIO()
        subprocess.call.return_value = 0
        url = 'http://example.com/auth/'
        subject = AuthConsoleUi(stdin, stdout, stderr, subprocess)
        result = subject.prompt_for_code(url)
        self.assertEqual('a code', result)
        subprocess.call.assert_called_with(['open', url])
        self.assertFalse(url in stdout.getvalue())

    def test_cant_open(self):
        subprocess = Mock()
        stdin = StringIO('a code')
        stdout = StringIO()
        stderr = StringIO()
        subprocess.call.return_value = 1
        url = 'http://example.com/auth/'
        subject = AuthConsoleUi(stdin, stdout, stderr, subprocess)
        result = subject.prompt_for_code(url)
        self.assertEqual('a code', result)
        subprocess.call.assert_called_with(['open', url])
        self.assertTrue(url in stdout.getvalue())
