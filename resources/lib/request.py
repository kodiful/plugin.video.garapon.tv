# -*- coding: utf-8 -*-

import hashlib

import urllib.request
import urllib.error

from urllib.parse import urlencode

from resources.lib.common import Common


class Request():

    def __init__(self):
        # 設定をコピー
        self.settings = {}
        for key in ('id', 'pw', 'auto', 'addr', 'http', 'https', 'session'):
            self.settings[key] = Common.GET('garapon_%s' % key)
        # サーバアドレス
        self.server = 'http://%s' % self.settings['addr']
        if self.settings['http']:
            self.server = '%s:%s' % (self.server, self.settings['http'])

    def __request(self, url, data=None):
        try:
            if data:
                if isinstance(data, bytes):
                    pass
                elif isinstance(data, str):
                    data = data.encode(encoding='utf-8', errors='ignore')
                else:
                    raise TypeError
                response = urllib.request.urlopen(urllib.request.Request(url, data))
            else:
                response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            Common.log('HTTPError: %s' % str(e.code), error=True)
            Common.notify('Request failed')
            return
        except urllib.error.URLError as e:
            Common.log('URLError: %s' % str(e.reason), error=True)
            Common.notify('Request failed')
            return
        response_body = response.read()
        response.close()
        return response_body

    def getgtvaddress(self):
        url = 'http://garagw.garapon.info/getgtvaddress'
        args = {'dev_id': Common.DEV_ID, 'user': self.settings['id'], 'md5passwd': hashlib.md5(self.settings['pw'].encode()).hexdigest()}
        return self.__request(url, urlencode(args)).decode(encoding='utf-8', errors='ignore')

    def auth(self):
        args = {'dev_id': Common.DEV_ID}
        url = '%s/gapi/v3/auth?%s' % (self.server, urlencode(args))
        args = {'type': 'login', 'loginid': self.settings['id'], 'password': self.settings['pw']}
        return self.__request(url, urlencode(args)).decode(encoding='utf-8', errors='ignore')

    def channel(self):
        args = {'dev_id': Common.DEV_ID, 'gtvsession': self.settings['session']}
        url = '%s/gapi/v3/channel?%s' % (self.server, urlencode(args))
        return self.__request(url).decode(encoding='utf-8', errors='ignore')

    def search(self, query):
        args = {'dev_id': Common.DEV_ID, 'gtvsession': self.settings['session']}
        url = '%s/gapi/v3/search?%s' % (self.server, urlencode(args))
        return self.__request(url, query).decode(encoding='utf-8', errors='ignore')

    def favorites(self, query):
        args = {'dev_id': Common.DEV_ID, 'gtvsession': self.settings['session']}
        url = '%s/gapi/v3/favorite?%s' % (self.server, urlencode(args))
        return self.__request(url, query).decode(encoding='utf-8', errors='ignore')

    def thumbnail(self, gtvid):
        url = self.thumbnail_url(gtvid)
        return self.__request(url)

    def thumbnail_url(self, gtvid):
        url = '%s/thumbs/%s' % (self.server, gtvid)
        return url

    def content_url(self, gtvid, starttime=0):
        args = {'dev_id': Common.DEV_ID, 'gtvsession': self.settings['session'], 'starttime': starttime}
        if gtvid[-5:] != '.m3u8':
            gtvid += '.m3u8'
        url = '%s/%s?%s' % (self.server, gtvid, urlencode(args))
        return url
