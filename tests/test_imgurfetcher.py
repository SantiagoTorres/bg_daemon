#!/usr/bin/env python
"""
    test_imgurfetcher

    Test suite for the imgurfetcher class
"""
import unittest
import bg_daemon.fetchers.imgurfetcher as imgurfetcher
import requests
import imgurpython
import random

from os.path import dirname, abspath, join
from mock import patch, mock_open, Mock

NUMBER_OF_IMAGES = 500


def fake_iter_content(reference=None, chunk_size=1, decode_unicode=False):

    return "flibble"


class test_imgurfetcher(unittest.TestCase):

    fetcher = None
    gallery = None
    albums = None
    mock_client = None
    settings_path = None
    bad_image_height = None
    bad_image_width = None
    bad_image_title = None
    bad_image_description = None
    good_image = None
    fake_response = None

    def setUp(self):

        self.settings_path = join(dirname(abspath(__file__)), "settings.json")
        self.fetcher = imgurfetcher.imgurfetcher(self.settings_path)
        self.gallery = []

        for i in range(NUMBER_OF_IMAGES):
            self.gallery.append(imgurpython.helpers.GalleryImage(
                link=self._generate_title(),
                title=self._generate_title(),
                description=self._generate_title(),
                width=random.randint(100, 10000),
                height=random.randint(100, 10000)))

        # we create a proper image that passes all tests
        self.gallery[-1].title = " ".join(self.fetcher.keywords)
        self.gallery[-1].description = " ".join(self.fetcher.keywords)

        # create some template bad/good images for testing
        self.bad_image_height = imgurpython.helpers.GalleryImage(link=None,
                title=self.fetcher.keywords[0],
                description=self.fetcher.keywords[0],
                width=10000, height=1)

        self.bad_image_width = imgurpython.helpers.GalleryImage(link=None,
                title=self.fetcher.keywords[0],
                description=self.fetcher.keywords[0],
                width=1, height=10000)

        self.bad_image_title = imgurpython.helpers.GalleryImage(link=None,
                title=self.fetcher.blacklist_words[0],
                description=self.fetcher.keywords[0],
                width=1000, height=10000)

        self.bad_image_description = imgurpython.helpers.GalleryImage(
                link=None,
                title=self.fetcher.keywords[0],
                description=self.fetcher.blacklist_words[0],
                width=1000, height=10000)

        self.good_image = self.gallery[-1]

        # we populate a dummy album for testing
        self.album = imgurpython.helpers.GalleryAlbum()
        self.album.id = 1

        # we monkeypatch the iter content method
        self.fake_response = Mock(spec=requests.Response)
        self.fake_response.iter_content = fake_iter_content

    def test_build_query(self):
        """
        Tests the private helper to build a query
        Tests for:
            * input sanitation
            * a proper query string is formed

        we test for both methods, recent and keyword

        Keyword:

            since query strings are randomized, we don't check the actual
            content of the query, but that everything is part of the
            settings...

        Recent:

            * We just verify that the query is simple (subreddit tag or
              similar)

        """
        # we will test for input sanitation.
        self.fetcher.mode = 'keywords'
        keywords_backup = self.fetcher.keywords
        self.fetcher.keywords = None

        with self.assertRaises(ValueError):
            self.fetcher._build_query()

        # verify that keywords is a list
        self.fetcher.keywords = 10
        with self.assertRaises(ValueError):
            self.fetcher._build_query()

        self.fetcher.keywords = keywords_backup
        query = self.fetcher._build_query()

        self.assertTrue(query is not None)
        self.assertTrue(isinstance(query, str))

        for word in query.strip().split():

            is_here = False

            if word in self.fetcher.keywords:
                is_here = True
            elif word in self.fetcher.subreddits:
                is_here = True

            self.assertTrue(word not in self.fetcher.blacklist_words)
            self.assertTrue(is_here)

        # test for recent mode mode
        self.fetcher.mode = "recent"
        query = self.fetcher._build_query()

        self.assertTrue(query is not None)
        self.assertTrue(isinstance(query, str))

        for word in query.strip().split():

            is_here = False

            if word in self.fetcher.keywords:
                is_here = True
            elif word in self.fetcher.subreddits:
                is_here = True

            self.assertTrue(word not in self.fetcher.blacklist_words)
            self.assertTrue(is_here)

    def test_select_image(self):
        """
        Tests for the select image to filter filenames properly.

        Tests for:
            * Pick anything if there are no blacklist
            * Pick something that's not in the blacklist
            * Picking an image from an album
            * Wrong type on input
            * A large randomized query without a valid candidate returns None
            * Size constraints are met when selecting.
            * If a gallery is found, search within the gallery first.
            * Keyword mode randomly selects an image from the gallery.
        """
        blacklist_backup = self.fetcher.blacklist_words
        self.fetcher.blacklist_words = None

        self.assertTrue(self.fetcher._select_image(self.gallery) is not None)

        self.fetcher.blacklist_words = blacklist_backup
        self.assertTrue(self.fetcher._select_image(self.gallery) is not None)

        selected = self.fetcher._select_image(self.gallery)

        for word in selected.title.strip().split():
            self.assertTrue(word not in self.fetcher.blacklist_words)

        # trigger an index error when there is no image, and return None
        result = self.fetcher._select_image([])
        self.assertTrue(result is None)

        self.fetcher.min_width = 1000
        self.fetcher.min_height = 1000
        # trigger rejecting bc of width
        result = self.fetcher._select_image([self.bad_image_width,
                                             self.good_image])
        self.assertEquals(result, self.good_image)

        # trigger rejecting bc of height
        result = self.fetcher._select_image([self.bad_image_height,
                                             self.good_image])
        self.assertEquals(result, self.good_image)

        # trigger rejecting bc of title
        result = self.fetcher._select_image([self.bad_image_title,
                                             self.good_image])
        self.assertEquals(result, self.good_image)

        # trigger rejecting bc of description
        result = self.fetcher._select_image([self.bad_image_description,
                                             self.good_image])
        self.assertEquals(result, self.good_image)

        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.get_album_images
            mock_method.return_value = [self.good_image]

            result = self.fetcher._select_image([self.album])

            mock_method.assert_called_once_with(self.album.id)
            self.assertEquals(result, self.good_image)

            # the album returns non-working images... it should seek more, but
            # that's it.
            mock_method.return_value = []
            result = self.fetcher._select_image([self.album])
            self.assertTrue(result is None)

            # now try with an image right after it, we should select the last
            # image
            result = self.fetcher._select_image([self.album, self.good_image])
            self.assertEquals(result, self.good_image)

            # finally, imagine that the get_album_image method breaks and
            # returns none
            mock_method.return_value = None
            result = self.fetcher._select_image([self.album, self.good_image])
            self.assertEquals(result, self.good_image)

        # Test for keyword mode
        self.fetcher.mode = "keywords"
        result = self.fetcher._select_image([self.good_image])
        self.assertEquals(result, self.good_image)

        # test that the fetcher gives up on 30 attempts
        result = self.fetcher._select_image([self.bad_image_title]*50)
        self.assertTrue(result is None)

        # return everything to normal
        self.fetcher.mode = "recent"

    def test_get_image_from_album(self):
        """
        Tests for input sanity and proper output on the galleryAlbum
        helper.

        Tests included here are:

            * Wrong typed input
            * A proper invocation method returns an expected image.
        """
        with self.assertRaises(ValueError):
            self.fetcher._get_image_from_album(None)

        with self.assertRaises(ValueError):
            self.fetcher._get_image_from_album(self.gallery[0])

        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.get_album_images
            mock_method.return_value = [self.good_image]

            result = self.fetcher._get_image_from_album(self.album)

            mock_method.assert_called_once_with(self.album.id)
            self.assertEquals(result, self.good_image)

    def test_constructor(self):
        """
            tests that the constructor works properly:

            Tests included here are:

                * Wrong typed arguments to the constructor
                * Wrong/corrupted version of the settings file
                * That the default method is "recent"
        """
        # test for wrong argument for settings file
        with patch("bg_daemon.fetchers.imgurfetcher.os.path.join") as \
                mock_method:

            mock_method.return_value = None

            with self.assertRaises(TypeError):
                dummy_fetcher = imgurfetcher.imgurfetcher(None)

        # test for corrupted json file
        with patch("bg_daemon.fetchers.imgurfetcher.json.load") as mock_method:

            # we write a json file that tries to overwrite the save method
            corrupted_json = {"fetcher": {"query": None}}
            mock_method.return_value = corrupted_json

            with self.assertRaises(ValueError):
                dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)

        # test for a "recent" mode fallback when initializing
        with patch("bg_daemon.fetchers.imgurfetcher.json.load") as mock_method:

            corrupted_json = {"fetcher": {"mode": "nonexistent"}}
            mock_method.return_value = corrupted_json

            dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)
            self.assertTrue(dummy_fetcher.mode is "recent")

            corrupted_json = {"fetcher": {"mode": None}}
            mock_method.return_value = corrupted_json

            dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)
            self.assertTrue(dummy_fetcher.mode is "recent")

    def test_query(self):
        """
            test the query method:

            Tests that the query method does:

                * That imgurpython returns something unexpected
                * That imgurpython returns something valid and is properly
                  selected.
        """
        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.gallery_search
            mock_method.return_value = None

            # simulate that the datasource does not return something standard
            result = self.fetcher.query()
            self.assertTrue(result is None)
            mock_method.assert_called_once()

            # Simulate that the datasource returns an empty gallery
            mock_method.return_value = []
            result = self.fetcher.query()
            self.assertTrue(result is None)
            mock_method.assert_called_once()

            # simulate a valid query
            mock_method.return_value = [self.good_image]
            result = self.fetcher.query()
            self.assertEquals(result, self.good_image)
            mock_method.assert_called_once()

    def test_fetch(self):
        """
        test for the "fetch" method

        we verify that:
            * Input sanitation is performed properly
            * The request is made to the proper link
            * The file extension is appended if not in the link
              (jpg is hardcoded)
            * The request object returns a valid iterable
            * Weird image titles are handled properly
        """
        imgobject = imgurpython.helpers.GalleryImage(link=None,
                                                     title="Neat mountains",
                                                     description="or not",
                                                     width=10000, height=10000)

        # verify that we can only send imgur objects here
        with self.assertRaises(ValueError):
            self.fetcher.fetch(None, "filename")

        with self.assertRaises(ValueError):
            self.fetcher.fetch("badtype", "filename")

        # verify that we send a proper filename here
        with self.assertRaises(ValueError):
            self.fetcher.fetch(imgobject, None)

        with self.assertRaises(ValueError):
            self.fetcher.fetch(imgobject, 10)

        # check that the request is properly formatted
        with patch("bg_daemon.fetchers.imgurfetcher.requests.get") as \
                mock_method:

            mock_method.return_value = None
            imgobject.link = None

            # we check that the link is properly checked when building
            # the request
            with self.assertRaises(ValueError):
                self.fetcher.fetch(imgobject, "filename.jpg")

            mock_method.return_value = self.fake_response
            open_mock = mock_open()
            with patch("bg_daemon.fetchers.imgurfetcher.open", open_mock,
                       create=True):

                # Assert that we actually try to write the file
                self.fetcher.fetch(imgobject, "filename.jpg")
                open_mock.assert_called_once_with("filename.jpg", "wb")

            open_mock = mock_open()
            with patch("bg_daemon.fetchers.imgurfetcher.open", open_mock,
                       create=True):
                # Assert that it tries to infer a different extension if
                # not provided
                imgobject.link = "filename.gif"
                self.fetcher.fetch(imgobject, "filename")
                open_mock.assert_called_once_with("filename.gif", "wb")

    def _generate_title(self):

        with_blacklist = True if random.random() > .6 else False
        with_sub = True if random.random() > .5 else False
        with_keywords = random.randint(0, len(self.fetcher.keywords))

        blacklist = ''
        if with_blacklist:
            blacklist += random.choice(self.fetcher.blacklist_words)

        sub = ''
        if with_sub:
            sub += random.choice(self.fetcher.subreddits)

        keywords = ''
        for i in range(0, with_keywords):
            keywords += "{} ".format(random.choice(self.fetcher.keywords))

        return "{} {} {}".format(blacklist, sub, keywords)

if __name__ == '__main__':
    unittest.main()
