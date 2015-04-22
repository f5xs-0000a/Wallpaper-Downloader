__author__ = 'f5xs'

from level1 import area_check, BytesIO, currenttime, dim_check, exists, findall, LinkList, loads,  \
    mkdir, randint, remove, wallpaper_dir, config_file, Thread, UnexpectedFewThreadsError, enumerateT, Config
from level2 import Req, image_check, Link, Sleep
from pickle import load, dump
from requests.exceptions import HTTPError

"""
Transform this piece of code (including Level 4) into an object-oriented code that uses a single class (or more) to
  control all the queued, parsable, and rejected links and the domain data.
"""


class Downloader(object):
    def __init__(self, keep_alive=False):
        self.domains = {self._4chan, self.konachan, }
        self.stopped = set()
        if not exists(config_file):
            print('%s"links.json" not detected. Creating file...' % currenttime())
            self.links = Config()
            dump(self.links, open(config_file, "wb"))
        else:
            self.links = load(open(config_file, "rb"))
        self.statistics = {domain.__name__: {"downloaded": 0, "saved": 0} for domain in self.domains}
        self.__main__(keep_alive)
        # Time downloading, total images saved/downloaded, etc.

    def __main__(self, keep_alive=False):
        for domain in self.domains:
            Thread(target=self.automator, args=(domain, keep_alive), name=domain.__name__, daemon=True).start()
        try:
            Sleep(15, True).join()
            while True:
                if False in [name in [thread.name for thread in enumerateT()]
                             for name in [domain.__name__ for domain in self.domains.difference(self.stopped)]]:
                    raise UnexpectedFewThreadsError
                if self.domains == self.stopped:
                    raise SystemExit
                sleep_ = Sleep(15, True)
                self.links_writer()
                sleep_.join()
        except KeyboardInterrupt:
            print("%sKeyboardInterrupt caught. Shutting down..." % currenttime())
            self.links_writer()
            raise SystemExit
        except SystemExit:
            self.links_writer()
            raise
        except UnexpectedFewThreadsError:
            print("%sAn unexpected deletion of threads detected. Shutting down..." % currenttime())
            self.links_writer()
            raise SystemExit
        finally:
            string = "\nStatistics:\n"
            for domain in self.domains:
                string += "\n"
                string += "%s:\nSaved:       %s\nDownloaded:  %s\n" % (domain.__name__,
                                                                       self.statistics[domain.__name__]["saved"],
                                                                       self.statistics[domain.__name__]["downloaded"])
            print(string)

    def links_writer(self):
        try:
            open(config_file, "rb")
        except FileNotFoundError:
            print("%sPlease stop deleting %s while the program is running." % (currenttime(), config_file))
        dump(self.links, open("%s.bak" % config_file, "wb"))
        dump(self.links, open("%s" % config_file, "wb"))
        remove("%s.bak" % config_file)
        print("%s%s overwritten." % (currenttime(), config_file))

    def image_downloader(self, domainname):
        if domainname not in self.links.queue:
            return
        site = self.links.queue[domainname]
        if isinstance(site, type(LinkList)):
            raise TypeError("Expected type LinkList, not %s" % type(site))
        while not site.empty():
            link = site.get()
            filetype = findall(r"(?<=\.)\w*$", link.link)[0]
            if domainname == "konachan":
                indexnum = findall(r"(?<=Konachan\.com%20-%20)\d*", link.link)[0]
            elif domainname == "_4chan":
                indexnum = findall(r"\d*(?=\.\w*$)", link.link)[0]
            elif domainname == "_8chan":
                indexnum = findall(r"(?<=\/)\d*(?=\.)", link.link)[0]
            else:
                indexnum = randint(0, 999999999)
            try:
                download = Req(link.link, bulk=True)
                self.statistics[domainname]["downloaded"] += 1
                if image_check(BytesIO(download.content), "dimensions", "colors", "size"):
                    if not exists("%s" % wallpaper_dir):
                        mkdir("%s" % wallpaper_dir)
                    if not exists("%s/%s" % (wallpaper_dir, link.dimstr())):
                        mkdir("%s/%s" % (wallpaper_dir, link.dimstr()))
                    with open("%s/%s/%s %s.%s" % (wallpaper_dir, link.dimstr(), domainname, indexnum, filetype),
                              "wb") as image_file:
                        image_file.truncate()
                        image_file.write(download.content)
                        image_file.flush()
                        self.statistics[domainname]["saved"] += 1
            except HTTPError:
                pass
            self.links.queue[domainname].rm()

    def automator(self, domain, keep_alive=False):
        token = False
        try:
            cutoff = self.links.data[domain.__name__]
        except KeyError:
            cutoff = None
        while True:
            if domain.__name__ not in self.links.getlinks:
                self.links.getlinks[domain.__name__] = True
            if not self.links.getlinks[domain.__name__]:
                self.image_downloader(domain.__name__)
            self.links.getlinks[domain.__name__] = True
            if token and not keep_alive:
                print("%sEnding %s downloader." % (currenttime(), domain.__name__))
                break
            token = False
            if cutoff:
                if domain.__name__ == "_4chan":
                    domain(cutoff=cutoff, disable_imt=True, disable_odt=True)
                else:
                    domain(cutoff=cutoff)
            else:
                domain()
            self.links.getlinks[domain.__name__] = False
            token = True
        self.stopped.add(domain)

    # Beyond this point are functions that would get the links of images from given domains

    def _4chan(self, cutoff=0, boards=("wg", "w"), disable_imt=False, disable_odt=False):
        threads = []
        lastpost = 0
        for board in boards:
            request = Req("http://a.4cdn.org/%s/threads.json" % board, str_data=True)
            for page in loads(request.text):
                for thread in page["threads"]:
                    threads.append((board, thread["no"]))
        for thread in threads:
            request = Req("http://a.4cdn.org/%s/thread/%s.json" % (thread[0], thread[1]), str_data=True)
            for post in loads(request.text)["posts"]:
                if "sub" in post:
                    if (disable_imt and "IMT" in post["sub"]) or (disable_odt and "ODT" in post["sub"]):
                        break
                if False not in (key in post for key in ["w", "h", "tim", "ext"]):
                    if dim_check(post["w"], post["h"]) and area_check(post["w"], post["h"]) and post["tim"] > cutoff \
                            and post["ext"].lower() in (".jpg", ".jpeg", "png"):
                        if "_4chan" not in self.links.queue:
                            self.links.queue["_4chan"] = LinkList()
                        self.links.queue["_4chan"].add(Link("http://i.4cdn.org/%s/%s%s" % (thread[0], post["tim"],
                                                                                           post["ext"]),
                                                            post["w"], post["h"]))
                    if post["tim"] > lastpost:
                        lastpost = post["tim"]
        try:
            if lastpost > self.links.data["_4chan"]:
                self.links.data["_4chan"] = lastpost
        except KeyError:
            self.links.data["_4chan"] = lastpost
        except NameError:
            pass

    def _8chan(self, cutoff=0, boards=("wg", "w", "wall")):
        # Fix the extra files issue with this.
        # Fix the file naming issue with this.
        # Reference: http://8ch.net/wg/res/%s.json
        threads = []
        lastpost = 0
        for board in boards:
            request = Req("http://8ch.net/%s/threads.json" % board, str_data=True)
            for page in loads(request.text):
                for thread in page["threads"]:
                    threads.append((board, thread["no"]))
        for thread in threads:
            request = Req("http://8ch.net/%s/res/%s.json" % (thread[0], thread[1]), str_data=True)
            for post in loads(request.text)["posts"]:
                if False not in (key in post for key in ["w", "h", "tim", "ext"]):
                    post["tim"] = int(post["tim"])
                    if dim_check(post["w"], post["h"]) and area_check(post["w"], post["h"]) and post["tim"] > cutoff \
                            and post["ext"].lower() in (".jpg", "jpeg", "png"):
                        if "_8chan" not in self.links.queue:
                            self.links.queue["_8chan"] = LinkList()
                        self.links.queue["_8chan"].add(Link("http://media.8ch.net/%s/src/%s%s" %
                                                            (thread[0], post["tim"], post["ext"]),
                                                            post["w"], post["h"]))
                        if post["tim"] > lastpost:
                            lastpost = post["tim"]

    def konachan(self, cutoff=0):
        page = 1
        max_index = cutoff
        while True:
            request = loads(Req("http://konachan.com/post.json", params={"limit": 100, "page": page}, str_data=True).
                            text)
            if not request:
                self.links.data["konachan"] = max_index
                return
            for post in request:
                if post["id"] <= cutoff:
                    self.links.data["konachan"] = max_index
                    return
                else:
                    if dim_check(post["width"], post["height"]) and area_check(post["width"], post["height"]):
                        if "konachan" not in self.links.queue:
                            self.links.queue["konachan"] = LinkList()
                        else:
                            self.links.queue["konachan"].add(Link(post["file_url"], post["width"], post["height"]))
                    else:
                        if "konachan" not in self.links.rejected:
                            self.links.rejected["konachan"] = LinkList()
                        self.links.rejected["konachan"].add(Link(post["file_url"], post["width"], post["height"]))
                if post["id"] > max_index:
                    max_index = post["id"]
            page += 1
# ============

if __name__ == "__main__":
    Downloader(False)
