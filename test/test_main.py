import unittest
from mock import Mock, patch
from tempfile import mkdtemp
from shutil import rmtree
from StringIO import StringIO
import time
import os
import main

@patch('main.photo.download')
@patch('main.containers.download')
@patch('main.photolist.download')
@patch('main.authenticate')
class TestMain(unittest.TestCase):
    def setUp(self):
        self.dir = mkdtemp()

    def tearDown(self):
        rmtree(self.dir)

    def test_aborts_when_photolist_fails(self, authenticate,
            download_photolist, download_containers, download_photos):
        download_photolist.return_value = None
        output = StringIO()
        main.flickr_to_go(self.dir, False, '', '', output)
        download_containers.assert_not_called()
        download_photos.assert_not_called()

    @patch('time.time')
    def test_saves_timestamp_on_success(self, get_time, authenticate,
            download_photolist, download_containers, download_photos):
        get_time.side_effect = [1461270854.6, 1461271102]
        output = StringIO()
        ok = main.flickr_to_go(self.dir, False, '', '', output)
        self.assertTrue(ok)
        with open(os.path.join(self.dir, 'timestamp')) as f:
            self.assertEqual('1461270855', f.read())
        pass
