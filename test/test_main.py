import unittest
from mock import Mock, patch
from tempfile import mkdtemp
from shutil import rmtree
from StringIO import StringIO
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
