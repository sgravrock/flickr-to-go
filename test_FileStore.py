import unittest
import sys
import json
import tempfile
import shutil
import os
from contextlib import contextmanager
from mock import patch
from StringIO import StringIO
import storage

def raise_io_error(*args):
    raise IOError('nope!')

@contextmanager
def in_temp_dir():
    # TODO: use tempfile.TemporaryDirectory once ported to python 3
    dir = tempfile.mkdtemp()
    try:
        with pushd(dir):
            yield
    finally:
        shutil.rmtree(dir)

@contextmanager
def pushd(dest):
     src = os.getcwd()
     os.chdir(dest)
     try:
         yield
     finally:
         os.chdir(src)

class TestFileStore(unittest.TestCase):
    @patch('os.mkdir')
    @patch('storage.open')
    def test_save_json(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        subject.save_json('foo/bar.json', {})
        mock_mkdir.assert_called_with('root/foo')
        mock_open.assert_called_with('root/foo/bar.json', 'w')

    @patch('os.mkdir')
    @patch('storage.open')
    def test_save_image(self, mock_open, mock_mkdir):
        subject = storage.FileStore('root')
        subject.save_image('foo.jpg', '')
        mock_open.assert_called_with('root/foo.jpg', 'wb')

    @patch('os.mkdir')
    @patch('storage.open')
    @patch('os.path.exists')
    def test_exists(self, mock_exists, mock_open, mock_mkdir):
        mock_exists.return_value = True
        subject = storage.FileStore('root')
        self.assertTrue(subject.exists('foo'))
        mock_exists.assert_called_with('root/foo')
        mock_exists.return_value = False
        self.assertFalse(subject.exists('foo'))

    def test_saved_credentials_some(self):
        with in_temp_dir():
            orig_creds = {'token': 'foo', 'secret': 'bar'}
            subject = storage.FileStore('somedir')
            subject.save_credentials(orig_creds)
            loaded_creds = subject.saved_credentials()
            self.assertEqual(loaded_creds, orig_creds)
            self.assertTrue(os.path.exists('somedir/flickr-credentials'))

    def test_saved_credentials_none(self):
        with in_temp_dir():
            subject = storage.FileStore('somedir')
            self.assertFalse(subject.saved_credentials())

