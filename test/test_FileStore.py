import unittest
import sys
import json
from mock import patch
from StringIO import StringIO
import storage

def raise_io_error(*args):
    raise IOError('nope!')

@patch('os.mkdir')
@patch('storage.open')
class TestFileStore(unittest.TestCase):
    def test_save_json(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        subject.save_json('foo/bar', {})
        mock_mkdir.assert_called_with('root/foo')
        mock_open.assert_called_with('root/foo/bar.json', 'w')

    def test_save_image(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        subject.save_image('foo.jpg', '')
        mock_open.assert_called_with('root/foo.jpg', 'wb')

    @patch('os.path.exists')
    def test_exists(self, mock_exists, mock_open, mock_mkdir):
        mock_exists.return_value = True
        subject = storage.FileStore('root')
        self.assertTrue(subject.exists('foo'))
        mock_exists.assert_called_with('root/foo')
        mock_exists.return_value = False
        self.assertFalse(subject.exists('foo'))

    def test_credentials_path(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        self.assertEqual('root/flickr-credentials',
                subject.credentials_path())

    def test_has_saved_credentials_true(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        self.assertTrue(subject.has_saved_credentials());
        mock_open.assert_called_with('root/flickr-credentials')

    def test_has_saved_credentials_false(self, mock_open, mock_mkdir):
        mock_open.side_effect = raise_io_error
        subject = storage.FileStore('root')
        self.assertFalse(subject.has_saved_credentials());
        mock_open.assert_called_with('root/flickr-credentials')
