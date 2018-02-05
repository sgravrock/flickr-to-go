import unittest
import sys
import json
import tempfile
import shutil
import os
from contextlib import contextmanager
import storage

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
    def test_save_json(self):
        with in_temp_dir():
            os.mkdir('root')
            subject = storage.FileStore('root')
            subject.save_json('foo/bar.json', {})
            with open('root/foo/bar.json') as f:
                self.assertEqual({}, json.load(f))

    def test_save_image(self):
        with in_temp_dir():
            subject = storage.FileStore('root')
            subject.save_image('foo.jpg', '')
            self.assertTrue(os.path.exists('root/foo.jpg'))

    def test_exists(self):
        with in_temp_dir():
            subject = storage.FileStore('root')
            os.mkdir('root')
            self.assertFalse(subject.exists('foo'))
            with open('root/foo', 'w'):
                pass
            self.assertTrue(subject.exists('foo'))

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

