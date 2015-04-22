__author__ = 'f5xs'

from level1              import area_check, coprime, currenttime, delete_minimals, dim_check, freq_threshold, url_make,\
                                Sleep
from PIL                 import Image
from re                  import match, sub
from requests            import ConnectionError, get, Timeout
from requests.exceptions import ChunkedEncodingError, HTTPError
from threading           import Thread


def image_check(image_file, *args):
    image = Image.open(image_file)
    value = [False]

    def __init__(value):
        try:
            if "dimension" in args:
                if dim_check(image.size[0], image.size[1]):
                    pass
                else:
                    return
            if "colors" in args:
                if not delete_minimals:
                    pass
                elif max([color[0] for color in image.getcolors(image.size[0]*image.size[1])]) / \
                        (image.size[0]*image.size[1]) < freq_threshold:
                    pass
                else:
                    return
            if "size" in args:
                if area_check(image.size[0], image.size[1]):
                    pass
                else:
                    return
            value[0] = True
        except MemoryError:
            return

    thread = Thread(target=__init__, args=(value,))
    thread.daemon = True
    thread.start()
    thread.join(8)
    return value[0]


class Req(object):
    # An object that downloads a given URL continuously and will not return errors.

    def __init__(self, url, str_data=False, cooldown=1, error_limit=4, timeout=(4, 2), clip=54,
                 print_=True, params={}, bulk=False, **kwargs):

        class CustomException(BaseException):
            pass

        link = url_make(url, params)
        sc_counter = 0
        lowerlimit = 0
        self.content = b''
        raised = False
        if print_:
            print("%sDownloading %s..." % (currenttime(), link[:(lambda: clip if clip else None)()]))
        while True:
            sleep_ = Sleep(cooldown, True)
            try:
                if bulk:
                    if "headers" in kwargs:
                        headers = kwargs["headers"]
                        del(kwargs["headers"])
                        if not match(r"bytes=\d*-", headers["range"]):
                            raise BaseException("Range header does not conform to 'bytes=[lowerlimit]-[upperlimit]"
                                                " format.")
                        if "range" in headers:
                            print("%sOverriding range upper limit." % currenttime())
                            lowerlimit = match(r"(?<=bytes=)\d*(?=-)", headers["range"])
                    else:
                        headers = {"range": "bytes=0-"}
                    headers["range"] = sub(r"(?<=bytes=)\d*(?=-)", str(lowerlimit + len(self.content)),
                                           headers["range"])
                    self.request = get(url, timeout=timeout, stream=True, params=params, headers=headers, **kwargs)
                    if "Content-Range" not in self.request.headers:
                        raise CustomException
                    for byte in self.request.iter_content(chunk_size=1024):
                        if byte:
                            self.content += byte
                    if str_data:
                        self.text = str(self.content)[2:-1]
                else:
                    self.request = get(url, timeout=timeout, stream=True, params=params, **kwargs)
                    self.content = self.request.content
                    if str_data:
                        self.text = self.request.text
                self.request.raise_for_status()
                self.status_code = self.request.status_code
                self.url = self.request.url
                self.headers = self.request.headers
                break
            except (ChunkedEncodingError, ConnectionError, Timeout) as err:
                raised, errmsg = True, err
            except HTTPError as err:
                raised, errmsg = True, err
                if int(self.request.status_code/100) == 4:
                    if self.request.status_code == 429:
                        pass
                    else:
                        raise
                else:
                    sc_counter += 1
                    if sc_counter >= error_limit:
                        raise
            except CustomException:
                bulk = False
                print("%sServer does not accept custom ranges. Restarting request." % currenttime())
            finally:
                if raised:
                    print("%sError: %s" % (currenttime(), errmsg))
                sleep_.join()

    def json(self):
        return self.request.json()



class Link(object):
    #       Here's a Blue Link: http://i.imgur.com/grmKzK1.jpg
    # And here's a Purple Link: http://i.imgur.com/B1vfIwx.png
    # HEEEYYYYAAAAAA!!!

    def __init__(self, link, width, height):
        self.link = link
        self.width, self.height = coprime(width, height)

    def __hash__(self):
        return self.link.__hash__()

    def __eq__(self, other):
        if not isinstance(other, Link):
            return False
        return self.link == other.link and self.width == other.width and self.height

    def __ne__(self, other):
        return not self.__eq__(other)

    def dimstr(self, dim_check=True, separator="×"):
        if dim_check:
            _ = self.dim_check()
            return str(_[0]) + separator + str(_[1])
        else:
            return str(self.width) + separator + str(self.height)

    def dim_check(self):
        return dim_check(self.width, self.height)