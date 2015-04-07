# bg\_daemon
An extensible python set of classes to update your background images.

[![Build Status](https://travis-ci.org/SantiagoTorres/bg_daemon.svg?branch=master)](https://travis-ci.org/SantiagoTorres/bg_daemon)
[![Coverage Status](https://coveralls.io/repos/SantiagoTorres/bg_daemon/badge.svg)](https://coveralls.io/r/SantiagoTorres/bg_daemon)

*Consider that this is not fully tested yet, if you encounter anything
unexpected please let me know*

# Installation

Right now, you can simply run

```Bash
$ sudo ./setup.py install
```

Once the installation is done, you must add a cronjob. As of this time, I'm
working in an out of the box way to add a cronjob, in the meantime, you can
do the following from a python shell:

```python
>>> import bg_daemon.util
>>> bg_daemon.util.add_crontab_entry()
```

That's it, now it's installed.


## Configuration

The very first time that "background\_daemon.py" is called, it creates a
directory in your home called ".bg\_daemon". Inside it, you will find the
settings.json file. You can edit this file to modify the behavior of the
daemon.

### Setting up the fetcher

A fetcher is the module that's in charge of getting images from god knows
where and hand them to the polling daemon.

Right now, the only available fetcher is the imgur.com fetcher, so I will
describe it here.

#### Mode

Right now, the fetcher supports two "modes":

* "recent" (default): that fetches the latest image in a random subreddit
* "keywords": creates a random query from a list of keywords and a random
  subreddit

By setting the "mode" value here, you modify how the fetcher downloads images
from imgur.

##### Keywords

If you use the keywords mode, you can populate this list (see the example file),
with words that interest you to build queries.

#### Subreddits

You can populate this list with subreddits of interest, earthporn is a great
choice. Keep in mind that not all files are hosted in imgur, so they will
not be available (until someone writes a fetcher for that).

#### min_width, min_height

You can set a minimum size constraint so the images have a proper resoltuion.

#### blacklist\_words

You can set a list of values that you do not want to appear in the title,
or description of the image. Imgur can host some really nasty things, so
this seems to be a required feature.


### Setting up the daemon

#### Choosing a fetcher

The fetcher is dynamically loaded here, a string identifying the fetcher is
supplied to choose it. "imgurfetcher" is the only available option as of now.

#### Frequency

Here you define the time, in seconds, before changing the image. It defaults to
a minute, but it's a better idea to put it to, say, 3600 so it changes every
hour.


#### Retries and slack

It is possible that sometimes the fetcher fails (e.g., a 404, server is
overloaded, you lost connection, etc.), instead of failing silently, the
daemon can wait "slack" amount of time and retry up to "retires" times.

You can set slack to a low number to make it wait less between retries and
increase the number of retries if needed. *I'd advice to leave it in the
default values*.

#### Target

In simple words, where do you want to save this. It defaults to $HOME/.bg\_daemon/bg.jpg

#### Backup

If backup is "yes", then the daemon will backup the last image if there is any.
it will save the image in the same folder as the target and add a
"hashed-prefix" to the filename to uniquely identify each image.

In other words, it moves the old image to a new location before writing the new
one.

#### Update\_hook

In order to change the background you might need to call a command that updates
the background with the new image. I personally use 'feh' in linux, so you
can use it also.

*If you are using this on a mac, you should change this*

#### Env

The environment variables for the update\_hook. I wouldn't touch them unless
the system isn't working.




