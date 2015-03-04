#!/usr/bin/env python
import os
import datetime
import shutil
import json
import time
import subprocess, shlex
from imgurfetcher import imgurfetcher
"""
    Background daemon.

    Sleeps for some time. Sets a target date and downloads an image
    using a specified fetcher (imgur so far). Once the image has been
    received, replaces a background image or adds it to a specific folder.

    <Properties>
        fetcher:    The instance of the fetcher class. It downloads an image
                    based on some specified parameters

        target:     A folder or filename to which save the image if everything
                    worked out properly

        frequency:  How often should the fetcher get a new image?

        retries:    If it didn't get something from the fetcher, how many times
                    should it keep trying until it gets something?

        slack:      How long should we wait between tries?

        backup:     A boolean flag that's used upon saving to backup the
                    previous image

        update_hook:A command to call with "subprocess" once the image has
                    been placed correctly.

"""
class background_daemon:

    fetcher     = None
    target      = None
    frequency   = None
    retries     = None
    slack       = None
    backup      = None
    update_hook = None


    """
        __init__

        Loads filename (the settings file) and populates it with the pertinent
        information

        <Arguments>
            
            filename: The location of the settings file.
    """
    def __init__(self, filename = 'settings.json'):

        try:
            with open(filename) as fp:
                data = json.load(fp)
        except Exception as e:
            raise

        if 'daemon' in data:

            data = data['daemon']
            for key in data:

                if key == 'fetcher':
                    self.fetcher = imgurfetcher()
                    continue

                setattr(self, key, data[key])

            if self.backup == "yes":
                self.backup = True
            else:
                self.backup = False


    """ daemon

        Daemonizes this object and process to call poll every now and then...

        TODO: this
    """
    def daemon(self):

        pass

    """
        Update 

        Fetches an image and replaces it in the target file or folder.
    """
    def update(self):

        assert(isinstance(self.retries, int))
        assert(isinstance(self.fetcher, imgurfetcher))
        assert(isinstance(self.target, str) or isinstance(self.target, unicode))
        assert(isinstance(self.slack, int))

        self.target = str(self.target)

        for i in range(self.retries):

            query = self.fetcher.query()

            if query is not None:
                break

            time.sleep(self.slack)

        if query is None:
            return None

        if self.backup and not os.path.isdir(self.target):
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup_target = "{}.{}".format(self.target, timestamp)

            try:
                shutil.copyfile(self.target, backup_target)
            except:
                print("couldn't create backup image!")
                pass
   
        try:
            self.fetcher.fetch(query, self.target)
        except Exception as e:
            print("Fetcher error, couldn't fetch image!")
            if self.backup and not os.path.isdir(self.target):
                try:
                    shutil.copyfile(backup_target, self.target)
                    shutil.rmfile(backup_taget)
                except:
                    print("Couldn't load backup image!")
                    pass
            else:
                raise
       
        # Run the update command
        if self.update_hook:
            subprocess.call(shlex.split(self.update_hook))

    """
        poll method.

        Checks whether is time to update or not

    """
    def poll(self):
    
        print("Polling")
        if os.path.exists("timestamp") and os.path.isfile("timestamp"):
            with open("timestamp") as fp:
                timestamp = fp.read()
            
            try:
                updatedate = datetime.datetime.fromtimestamp(float(timestamp))
            except:
                print("timestamp is corrupted!, initializing...")
                return self._initialize_datetime()

            if datetime.datetime.now() > updatedate:
                print("updating")
                self.update()
                nexttimestamp = updatedate + datetime.timedelta(
                        seconds = self.frequency)
                
                with open("timestamp", "wt") as fp:
                    fp.write(nexttimestamp.strftime("%s"))

                return True

            else:
                return False

        else:
            print("No timestamp found! initializing...")
            return self._initialize_timestamp()

    """
        _initialize_timestamp()

        If the timestamp file is corrupted or missing, reconstruct it from
        now
    """
    def _initialize_timestamp(self):
        
        try:
            with open("timestamp", "wb") as fp:
                nexttimestamp = datetime.datetime.now() + datetime.timedelta(
                        seconds = self.frequency)
                fp.write(nexttimestamp.strftime("%s"))

            return True

        except:
            # TODO: error handling here could be friendlier
            raise


"""
    The main method is set to generate a new instance and call update. This
    is useful if you want to call it from a chrontab or whatever
"""
if __name__ == "__main__":
    daemon = background_daemon()
    daemon.poll()

