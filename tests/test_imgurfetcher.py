#!/usr/bin/env python
"""
    test_imgurfetcher

    Test suite for the imgurfetcher class
"""
import unittest
import bg_daemon.fetchers.imgurfetcher as imgurfetcher
import imgurpython
import random
import os

from mock import patch

NUMBER_OF_IMAGES = 500


class test_imgurfetcher(unittest.TestCase):

    fetcher = None
    gallery = None
    albums = None
    mock_client = None
    settings_path = None

    def setUp(self):

        self.settings_path = os.path.join(os.getcwd(), "tests",
                                          "settings.json")
        self.fetcher = imgurfetcher.imgurfetcher(self.settings_path)
        self.gallery = []

        for i in range(NUMBER_OF_IMAGES):
            self.gallery.append(imgurpython.helpers.GalleryImage(
                link=self._generate_title(),
                title=self._generate_title(),
                description=self._generate_title(),
                width=random.randint(100, 10000),
                height=random.randint(100, 10000)))

        # we create a proper that passes all tests
        self.gallery[-1].title = " ".join(self.fetcher.keywords)
        self.gallery[-1].description = " ".join(self.fetcher.keywords)

        # we populate a dummy album for testing
        self.album = imgurpython.helpers.GalleryAlbum()
        self.album.id = 1

    def tearDown(self):
        pass

    """
    Tests the private helper to build a query
    Tests for:
        * input sanitation
        * a proper query string is formed

    since query strings are randomized, we don't check the actual content of
    the query, but that everything is part of the settings...

    we tests for both methods, recent and keyword
    """
    def test_build_query(self):

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

        for word in query.strip().split(" "):

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

        for word in query.strip().split(" "):

            is_here = False

            if word in self.fetcher.keywords:
                is_here = True
            elif word in self.fetcher.subreddits:
                is_here = True

            self.assertTrue(word not in self.fetcher.blacklist_words)
            self.assertTrue(is_here)


    """
    Tests for the select image to filter filenames properly.

    Tests for:
        * Pick anything if there are no blacklist
        * Pick something that's not in the blacklist
        * Picking an image from an album
    """
    def test_select_image(self):

        blacklist_backup = self.fetcher.blacklist_words
        self.fetcher.blacklist_words = None

        self.assertTrue(self.fetcher._select_image(self.gallery) is not None)

        self.fetcher.blacklist_words = blacklist_backup
        self.assertTrue(self.fetcher._select_image(self.gallery) is not None)

        selected = self.fetcher._select_image(self.gallery)

        for word in selected.title.strip().split(" "):
            self.assertTrue(word not in self.fetcher.blacklist_words)

        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.get_album_images
            mock_method.return_value = [self.gallery[-1]]

            result = self.fetcher._select_image([self.album])

            mock_method.assert_called_once_with(self.album.id)
            self.assertTrue(result == self.gallery[-1])

    """
    Tests for input sanity and proper output on the galleryAlbum helper.
    """
    def test_get_image_from_album(self):

        with self.assertRaises(ValueError):
            self.fetcher._get_image_from_album(None)

        with self.assertRaises(ValueError):
            self.fetcher._get_image_from_album(self.gallery[0])

        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.get_album_images
            mock_method.return_value = [self.gallery[-1]]

            result = self.fetcher._get_image_from_album(self.album)

            mock_method.assert_called_once_with(self.album.id)
            self.assertTrue(result == self.gallery[-1])

    """
        tests that the constructor works properly
    """
    def test_constructor(self):

        # test for wrong argument for settings file
        with patch("bg_daemon.fetchers.imgurfetcher.os.path.join") as \
                mock_method:

            mock_method.return_value = None

            with self.assertRaises(TypeError):
                dummy_fetcher = imgurfetcher.imgurfetcher(None)

        # test for corrupted json file
        with patch("bg_daemon.fetchers.imgurfetcher.json.load") as mock_method:

            # we write a json file that tries to overwrite the save method
            corrupted_json = {"fetcher":{"query":None}}
            mock_method.return_value = corrupted_json

            with self.assertRaises(ValueError):
                dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)

        # test for a "recent" mode fallback when initializing
        with patch("bg_daemon.fetchers.imgurfetcher.json.load") as mock_method:

            corrupted_json = {"fetcher":{"mode":"nonexistent"}}
            mock_method.return_value = corrupted_json

            dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)
            self.assertTrue(getattr(dummy_fetcher, "mode") is "recent")

            corrupted_json = {"fetcher":{"mode":None}}
            mock_method.return_value = corrupted_json

            dummy_fetcher = imgurfetcher.imgurfetcher(self.settings_path)
            self.assertTrue(getattr(dummy_fetcher, "mode") is "recent")


    """
        test the query method
    """
    def test_query(self):

        pass

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
            mock_method.return_value = [self.gallery[-1]]
            result = self.fetcher.query()
            self.assertTrue(result == self.gallery[-1])
            mock_method.assert_called_once()

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
    def test_fetch(self):

        imgobject = imgurpython.helpers.GalleryImage(link=None,
                                                     title="Neat mountains",
                                                     description="or not",
                                                     width=10000, height=10000)



        # verify that we can only send imgur objects here
        with self.assertRaises(ValueError):
            self.fetcher.fetch(None,  "filename")

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
