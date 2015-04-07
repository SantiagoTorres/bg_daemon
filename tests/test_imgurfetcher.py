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

    def setUp(self):

        settings_path = os.path.join(os.getcwd(), "tests",  "settings.json")
        self.fetcher = imgurfetcher.imgurfetcher(settings_path)
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
    """
    def test_build_query(self):

        # we will test for input sanitation.
        keywords_backup = self.fetcher.keywords
        self.fetcher.keywords = None

        with self.assertRaises(Exception):
            self.fetcher._build_query()

        self.fetcher.keywords = 10

        with self.assertRaises(Exception):
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

        with self.assertRaises(AssertionError):
            self.fetcher._get_image_from_album(None)

        with self.assertRaises(AssertionError):
            self.fetcher._get_image_from_album(self.gallery[0])

        with patch("bg_daemon.fetchers.imgurfetcher.ImgurClient") as \
                mock_class:

            mock_method = mock_class.return_value.get_album_images
            mock_method.return_value = [self.gallery[-1]]

            result = self.fetcher._get_image_from_album(self.album)

            mock_method.assert_called_once_with(self.album.id)
            self.assertTrue(result == self.gallery[-1])

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
