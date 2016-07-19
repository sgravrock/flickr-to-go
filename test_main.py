import unittest
from mock import Mock, patch, ANY
from tempfile import mkdtemp
from shutil import rmtree
from StringIO import StringIO
import time
import os
import main

@patch('main.photo.download')
@patch('main.containers.download')
@patch('main.photolist.fetch_recently_updated')
@patch('main.photolist.download')
@patch('main.authenticate')
class TestMain(unittest.TestCase):
    def setUp(self):
        self.dir = mkdtemp()

    def tearDown(self):
        rmtree(self.dir)

    def test_aborts_when_photolist_fails(self, authenticate,
            download_photolist, fetch_recently_updated,
            download_containers, download_photos):
        download_photolist.return_value = None
        output = StringIO()
        main.flickr_to_go(self.dir, False, '', '', output)
        download_containers.assert_not_called()
        download_photos.assert_not_called()

    @patch('time.time')
    def test_saves_timestamp_on_success(self, get_time, authenticate,
            download_photolist, fetch_recently_updated,
            download_containers, download_photos):
        get_time.side_effect = [1461270854.6, 1461271102]
        ok = main.flickr_to_go(self.dir, False, '', '', StringIO())
        self.assertTrue(ok)
        with open(os.path.join(self.dir, 'timestamp')) as f:
            self.assertEqual('1461270855', f.read())

    @patch('time.time')
    def test_handles_existing_timestamp(self, get_time, authenticate,
            download_photolist, fetch_recently_updated,
            download_containers, download_photos):
        get_time.side_effect = [1461271102.7, 1461281278.3]
        with open(os.path.join(self.dir, 'timestamp'), 'w') as f:
            f.write('1461270855')
        photolist = download_photolist.return_value = [{'id': 42}]
        updated = fetch_recently_updated.return_value = [42]

        ok = main.flickr_to_go(self.dir, False, '', '', StringIO())

        self.assertTrue(ok)
        fetch_recently_updated.assert_called_with(1461270855, ANY, ANY)
        download_photos.assert_called_with(photolist, updated, ANY, ANY, ANY, ANY)
        with open(os.path.join(self.dir, 'timestamp')) as f:
            self.assertEqual('1461271103', f.read())

    def test_handles_nonexistent_timestamp(self, authenticate,
            download_photolist, fetch_recently_updated,
            download_containers, download_photos):
        photolist = download_photolist.return_value = [{'id': 42}]
        main.flickr_to_go(self.dir, False, '', '', StringIO())
        fetch_recently_updated.assert_not_called()
        download_photos.assert_called_with(photolist, [], ANY, ANY, ANY, ANY)
