__author__ = 'f5xs'

"""
Issues:
1. image_downloader will no longer handle overwriting the queue file. Another function that would be run every 15
        seconds and during Exception raises will handle it.
"""

from copy import deepcopy
from io import BytesIO
from json import dumps, loads
from os import getcwd, remove, mkdir
from os.path import exists
from PIL import Image
from random import randint
from re import match, sub, findall
from requests import ConnectionError, get, HTTPError, Timeout
from requests.exceptions import ChunkedEncodingError
from signal import alarm, SIGALRM, signal
from threading import Thread
from threading import enumerate as enumerateT
from time import localtime, sleep, strftime

cwd = getcwd()
dimensions = [(16, 9)]  # (8, 5)
dims_threshold = 1./512
freq_threshold = .125
size_threshold = 1366*768
wallpaper_dir = "%s/Wallpapers" % cwd
config_file = "links.f5xs"


currenttime = lambda: "[%s] " % (strftime("%H:%M:%S", localtime()))


def dim_check(width, height):
    for ar in dimensions:
        if float(ar[0])/ar[1]*(1-dims_threshold) <= float(width)/height <= float(ar[0])/ar[1]*(1+dims_threshold):
            return ar
    return None


area_check = lambda width, height: width*height > size_threshold


class Sleep(object):
    def __init__(self, duration, start=False):
        self.thread = Thread(target=(lambda: sleep(duration)), name="SleepThread", daemon=True)
        if start:
            self.start()

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()


def coprime(*args):
    for arg in args:
        if type(arg) != int:
            raise TypeError("All coprime arguments should be integers.")

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    return_value = gcd(args[0], args[1])
    for arg in args[2:]:
        return_value = gcd(return_value, arg)

    return tuple([int(arg/return_value) for arg in args])


class UnexpectedFewThreadsError(Exception):
    pass


url_make = lambda url, params: "%s?%s" % (url, "&".join(["%s=%s" % (key, params[key]) for key in params])) if params \
    else url


class LinkList(object):
    def __init__(self, type_=0):  # 0 for set and 1 for list
        if type_ == 0:
            self.links = set()
        elif type_ == 1:
            self.links = []
        else:
            raise RuntimeError("Invalid type.")

    def add(self, entry):
        if isinstance(self.links, set):
            self.links.add(entry)
        elif isinstance(self.links, list):
            self.links.append(entry)
        else:
            raise NotImplementedError

    def get(self, rm=False):
        if self.links:
            if rm:
                return self.links.pop()
            for _ in self.links:
                return _
        else:
            raise IndexError("Links attribute is empty!")

    def rm(self):
        if isinstance(self.links, set):
            self.links = self.links.difference({self.get()})
        elif isinstance(self.links, list):
            self.links.remove(self.get())
        #  rm = lambda self, entry: self.links.remove(entry)

    def load(self, links, type_=0, json=True):
        links_ = LinkList(type_)
        if json:
            links = loads(links)
        for link in links:
            links_.add(link)
        return links_

    def dump(self, links):
        links = list(links)
        return dumps(links)

    def recheck(self, sort=True):
        if isinstance(self.links, set):
            raise RuntimeError("Links attribute is already a set!")
        elif isinstance(self.links, list):
            if sort:
                self.links = sorted(list(set(self.links)))
            else:
                self.links = list(set(self.links))
        else:
            raise NotImplementedError

    empty = lambda self: False if self.links else True

    def __len__(self):
        return len(self.links)


class Config(object):
    def __init__(self, version=20150131):
        self.version = version
        self.parsable = LinkList()  # Links awaiting for download
        self.rejected = {}          # Links awaiting for parsing
        self.data = {}              # Links rejected for download given their corresponding aspect ratio
        self.queue = {}             # Latest index number of sites at which images were collected
        self.getlinks = {}          # True if still obtaining links. False otherwise.

        self.data["konachan"] = 0
        self.data["_4chan"] = 0
