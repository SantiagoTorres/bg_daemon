#!/usr/bin/env python
import random
import requests
import os
import json
import sys
import logging

from imgurpython import ImgurClient
from imgurpython.helpers import GalleryAlbum, GalleryImage
from bg_daemon.util import HOME

CLIENT_ID = "b0d705fbff41bc1"


class imgurfetcher:
    """
        imgurfetcher class

        Loads configuration parameters from settings.py and downloads/saves
        images from imgur based on it.

        <Properties>

            keywords: a list containing all of the special keywords, ex:
                ['autumn', 'leaves', 'red']

                This list will be randomized and permutted before querying

            subreddits: a list of "keywords" from subreddits (e.g. earthporn),
                        it's used as a second filter. I don't advice using this
                        feature yet.

            client_id: you will have to set this up so the API accepts your
                       request

            min_height: use the size of your screen here, so nothing is too
                        ugly

            min_width: same idea here

            max_size: if you want to save your bandwidth/disk-space

            blacklist_words: a list containing words that might hint something
                             you don't want to see (e.g., you want fall season,
                             not 'pain')

            mode: either "recent" or "keywords". Recent will get the most
                  recent image in the subreddit, while keywords will filter
                  and randomly select an image in it. If mode is not either,
                  it will default to recent.

        <Functions>

            query(): Finds a candidate gallery to download
            fetch(): From the candidate, get the image data.
    """
    keywords = None
    subreddits = None
    client_id = None
    min_height = None
    min_width = None
    max_size = None
    blacklist_words = None
    mode = None

    """
        __init__

        Loads filename (the settings file) and populates it with the pertinent
        information

        <Arguments>

            filename: The location of the settings file.
    """
    def __init__(self, filename=None):

        logger.debug("initializing fetcher")
        if not filename:
            filename = os.path.join(HOME, "settings.json")


        with open(filename) as fp:
            data = json.load(fp)

        if 'fetcher' in data:

            for key in data['fetcher']:
                if key == 'query' or key == 'fetch' or key == 'save':
                    raise ValueError("The settings file is corrupted!")

                setattr(self, key, data['fetcher'][key])

        if self.mode is None:
            self.mode = "recent"

        if self.mode != 'keywords' and self.mode != 'recent':
            self.mode = 'recent'

        # we are hardcoding this value since we don't expect it to change too
        # much
        self.client_id = CLIENT_ID

    """
        query

        Queries imgur for a random image based on the settings loaded

        <Parameters>
            None

        <Returns>
            An Imgur gallery object
    """
    def query(self):

        # build our query
        query = self._build_query()
        logger.info("Querying imgur with {}".format(query))

        # Download gallery data
        client = ImgurClient(self.client_id, None)
        data = client.gallery_search(query, sort='time', window='year',
                                     page=0)

        # if we didn't get anything back... tough luck
        if len(data) < 1:
            return None

        logger.info("Found successful query {}".format(query))

        return self._select_image(data)

    """
        fetch function

        Upon receiving a imgur object. Download the image to memory.

        <parameters>
            imgobject: the object image that should be returned from get
            filename:  the target filename. Where to save the file

        <Returns>
            True if everything is fine
    """
    def fetch(self, imgobject, filename):

        if imgobject is None:
            raise ValueError("ImgObject wasn't initialized properly!")

        if filename is None:
            raise ValueError("filename wasn't initialized properly!")

        if not isinstance(filename, str):
            raise ValueError("filename should be a string!")

        # title will be changed to ascii before saving
        title = imgobject.title.encode('ascii', 'replace')
        logger.info("Saving image {} to {}".format(title, filename))

        req = requests.get(imgobject.link)

        # if we aren't provided an extension, we will do it for you.
        if len(os.path.splitext(filename)[1]) == 0:
            root, ext = os.path.splitext(imgobject.link)
            filename = "{}{}".format(filename, ext)

        with open(filename, 'wb') as fp:
            for chunk in req.iter_content():
                fp.write(chunk)

        req.close()
        return True

    """
        _build_query

        builds a query for the query function

    """
    def _build_query(self):

        assert(self.keywords is not None and isinstance(self.keywords, list))

        subreddit = None

        # build subreddit list if available
        if self.subreddits is not None:
            assert(isinstance(self.subreddits, list))
            subreddit = random.choice(self.subreddits)

        if self.mode == 'keywords':
            # get a random number of keywords and build a query
            number_of_keywords = random.randint(1, 2)
            random.shuffle(self.keywords)
            keywords = self.keywords[:number_of_keywords]

        # we are in the "recent" mode
        else:
            keywords = []

        query = ''
        for keyword in keywords:
            query += "{} ".format(keyword)

        if subreddit:
            query += "{} ".format(subreddit)

        return query

    """
        _select_image

        from a given result of galleries, pick one that matches
    """
    def _select_image(self, galleries):

        # Try to pick an image in the gallery
        elected = False

        attempts = 0

        while not elected:

            logger.debug("Selecting image...")

            if self.mode == "keywords":
                selected_image = random.choice(galleries)
            else:
                try:
                    selected_image = galleries.pop(0)
                except IndexError:
                    return None

            # if the "image" is actually an album, try to get a valid candidate
            # image from it.
            if isinstance(selected_image, GalleryAlbum):
                selected_image = self._get_image_from_album(selected_image)
                if selected_image is None:
                    continue

            logger.debug("Selecting Image {}".format(selected_image.title))
            attempts += 1
            if attempts > 30:
                return None

            if selected_image.width < self.min_width:
                logger.debug("Rejecting due to width...")
                continue

            if selected_image.height < self.min_height:
                logger.debug("Rejecting due to height...")
                continue

            if self.blacklist_words is not None:

                blacklist_words = set(self.blacklist_words)
                title = set(selected_image.title.split())

                if len(blacklist_words.intersection(title)):

                    logger.debug("Rejecting due to blacklist_words...")
                    continue

                if selected_image.description is not None:
                    description = set(selected_image.description.split())
                    if len(blacklist_words.intersection(description)):
                        logger.debug("Rejecting due to blacklist_words...")
                        continue

            elected = True

        logger.debug("Selected image {}".format(selected_image))

        return selected_image

    """
        _get_image_from_album

        If the query results in an album, get an image from it.
    """
    def _get_image_from_album(self, album):

        if not isinstance(album, GalleryAlbum):
            raise ValueError("_get_image_from_album: album should be "
                             "a GalleryAlbum instance!")

        # Download gallery data
        client = ImgurClient(self.client_id, None)
        album_id = album.id

        images = client.get_album_images(album_id)

        # Try to select an appropriate image from this album, return the
        # first one that fits our criteria.
        if images is not None:
            return self._select_image(images)

        return None


logger = logging.getLogger("bg_daemon")

if __name__ == '__main__':

    f = imgurfetcher()
    image = f.query()
    if image is not None:
        f.fetch(image, sys.argv[1])
        print("Fetch successful!")
    else:
        print("Fetch unsuccessful! :(")
