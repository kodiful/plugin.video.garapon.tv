# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib, urllib2
import hashlib

from urllib2 import URLError, HTTPError

from common import notify,log
from const import Const

#-------------------------------------------------------------------------------
class Request():

    def __init__(self):
        # 設定をコピー
        self.settings = {}
        for key in ('id','pw','auto','addr','http','https','session'):
            self.settings[key] = Const.GET('garapon_%s' % key)
        # サーバアドレス
        self.server = 'http://%s' % self.settings['addr']
        if self.settings['http']: self.server = '%s:%s' % (self.server, self.settings['http'])

    def __request(self, url, data=None):
        if data:
            req = urllib2.Request(url, data)
        else:
            req = url
        try:
            response = urllib2.urlopen(req)
        except HTTPError, e:
            log('HTTPError: %s' % str(e.code), error=True)
            notify('Request failed')
            return
        except URLError, e:
            log('URLError: %s' % str(e.reason), error=True)
            notify('Request failed')
            return
        response_body = response.read()
        response.close()
        return response_body

    def getgtvaddress(self):
        url = 'http://garagw.garapon.info/getgtvaddress'
        values = {'dev_id':Const.DEV_ID, 'user':self.settings['id'], 'md5passwd':hashlib.md5(self.settings['pw']).hexdigest()}
        return self.__request(url, urllib.urlencode(values))

    def auth(self):
        values = {'dev_id':Const.DEV_ID}
        url = '%s/gapi/v3/auth?%s' % (self.server, urllib.urlencode(values))
        values = {'type':'login', 'loginid':self.settings['id'], 'password':self.settings['pw']}
        return self.__request(url, urllib.urlencode(values))

    def channel(self):
        values = {'dev_id':Const.DEV_ID, 'gtvsession':self.settings['session']}
        url = '%s/gapi/v3/channel?%s' % (self.server, urllib.urlencode(values))
        return self.__request(url)

    def search(self, query):
        values = {'dev_id':Const.DEV_ID, 'gtvsession':self.settings['session']}
        url = '%s/gapi/v3/search?%s' % (self.server, urllib.urlencode(values))
        return self.__request(url, query)

    def favorites(self, query):
        values = {'dev_id':Const.DEV_ID, 'gtvsession':self.settings['session']}
        url = '%s/gapi/v3/favorite?%s' % (self.server, urllib.urlencode(values))
        return self.__request(url, query)

    def thumbnail(self, gtvid):
        url = '%s/thumbs/%s' % (self.server, gtvid)
        return self.__request(url)

    def content_url(self, gtvid, starttime=0):
        values = {'dev_id':Const.DEV_ID, 'gtvsession':self.settings['session'], 'starttime':starttime}
        if gtvid[-5:] != '.m3u8': gtvid += '.m3u8'
        url = '%s/%s?%s' % (self.server, gtvid, urllib.urlencode(values))
        return url

    def sync(self, url, credential, gtvsession, authtime, authupdate):
        values = {'credential':credential, 'gtvsession':gtvsession, 'authtime':authtime, 'authupdate':authupdate}
        url = '%s?%s' % (url, urllib.urlencode(values))
        return self.__request(url)
