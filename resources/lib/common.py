# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import socket
import os
import xbmc
import xbmcaddon

# アドオン情報
addon = xbmcaddon.Addon()

# HTTP接続におけるタイムアウト(秒)
socket.setdefaulttimeout(60)

# 設定
settings = {
    # ガラポンTV開発者ID
    'dev_id': '64ee928bac3e56e810a613bd350e0275',
    # 1ページあたりの表示数
    'apage': 100
}

# ファイル/ディレクトリパス
PROFILE_PATH = xbmc.translatePath(addon.getAddonInfo('profile').decode('utf-8'))
PLUGIN_PATH = xbmc.translatePath(addon.getAddonInfo('path').decode('utf-8'))
RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
DB_PATH = xbmc.translatePath('special://database')

CACHE_PATH = os.path.join(PROFILE_PATH, 'cache')
if not os.path.isdir(CACHE_PATH): os.makedirs(CACHE_PATH)

DOWNLOAD_PATH = addon.getSetting('download_path')
DOWNLOAD_URL = addon.getSetting('download_url')
if not DOWNLOAD_URL.endswith('/'): DOWNLOAD_URL = DOWNLOAD_URL+'/'

SETTINGS_FILE = os.path.join(RESOURCES_PATH, 'settings.xml')
TEMPLATE_FILE = os.path.join(DATA_PATH, 'settings.xml')
GENRE_FILE = os.path.join(DATA_PATH, 'genre.js')

CHANNEL_FILE = os.path.join(PROFILE_PATH, 'channel.js')
SMARTLIST_FILE = os.path.join(PROFILE_PATH, 'smartlist.js')

RESUME_FILE = os.path.join(PROFILE_PATH, 'resume.js')

CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')


def notify(message, time=10000, image='DefaultIconError.png'):
    xbmc.executebuiltin('XBMC.Notification("Garapon TV","%s",%d,"%s")' % (message,time,image))


def addon_debug(message, level=xbmc.LOGNOTICE):
    debug = addon.getSetting('debug')
    if debug == 'true': addon_error(message, level)


def addon_error(message, level=xbmc.LOGERROR):
    try: xbmc.log(message, level)
    except: xbmc.log(message.encode('utf-8','ignore'), level)


def isholiday(day):

    holidays = {
        "2014-01-01":True,
        "2014-01-13":True,
        "2014-02-11":True,
        "2014-03-21":True,
        "2014-04-29":True,
        "2014-05-03":True,
        "2014-05-04":True,
        "2014-05-05":True,
        "2014-05-06":True,
        "2014-07-21":True,
        "2014-09-15":True,
        "2014-09-23":True,
        "2014-10-13":True,
        "2014-11-03":True,
        "2014-11-23":True,
        "2014-11-24":True,
        "2014-12-23":True,
        "2015-01-01":True,
        "2015-01-12":True,
        "2015-02-11":True,
        "2015-03-21":True,
        "2015-04-29":True,
        "2015-05-03":True,
        "2015-05-04":True,
        "2015-05-05":True,
        "2015-05-06":True,
        "2015-07-20":True,
        "2015-09-21":True,
        "2015-09-22":True,
        "2015-09-23":True,
        "2015-10-12":True,
        "2015-11-03":True,
        "2015-11-23":True,
        "2015-12-23":True,
        "2016-01-01":True,
        "2016-01-11":True,
        "2016-02-11":True,
        "2016-03-20":True,
        "2016-03-21":True,
        "2016-04-29":True,
        "2016-05-03":True,
        "2016-05-04":True,
        "2016-05-05":True,
        "2016-07-18":True,
        "2016-08-11":True,
        "2016-09-19":True,
        "2016-09-22":True,
        "2016-10-10":True,
        "2016-11-03":True,
        "2016-11-23":True,
        "2016-12-23":True,
        "2017-01-01":True,
        "2017-01-02":True,
        "2017-01-09":True,
        "2017-02-11":True,
        "2017-03-20":True,
        "2017-04-29":True,
        "2017-05-03":True,
        "2017-05-04":True,
        "2017-05-05":True,
        "2017-07-17":True,
        "2017-08-11":True,
        "2017-09-18":True,
        "2017-09-23":True,
        "2017-10-09":True,
        "2017-11-03":True,
        "2017-11-23":True,
        "2017-12-23":True,
        "2018-01-01":True,
        "2018-01-08":True,
        "2018-02-11":True,
        "2018-02-12":True,
        "2018-03-21":True,
        "2018-04-29":True,
        "2018-05-03":True,
        "2018-05-04":True,
        "2018-05-05":True,
        "2018-07-16":True,
        "2018-08-11":True,
        "2018-09-17":True,
        "2018-09-23":True,
        "2018-09-24":True,
        "2018-10-08":True,
        "2018-11-03":True,
        "2018-11-23":True,
        "2018-12-23":True,
        "2018-12-24":True,
        "2019-01-01":True,
        "2019-01-14":True,
        "2019-02-11":True,
        "2019-03-21":True,
        "2019-04-29":True,
        "2019-05-03":True,
        "2019-05-04":True,
        "2019-05-05":True,
        "2019-05-06":True,
        "2019-07-15":True,
        "2019-08-11":True,
        "2019-08-12":True,
        "2019-09-16":True,
        "2019-09-23":True,
        "2019-10-14":True,
        "2019-11-03":True,
        "2019-11-04":True,
        "2019-11-23":True,
        "2019-12-23":True,
        "2020-01-01":True,
        "2020-01-13":True,
        "2020-02-11":True,
        "2020-03-20":True,
        "2020-04-29":True,
        "2020-05-03":True,
        "2020-05-04":True,
        "2020-05-05":True,
        "2020-05-06":True,
        "2020-07-20":True,
        "2020-08-11":True,
        "2020-09-21":True,
        "2020-09-22":True,
        "2020-10-12":True,
        "2020-11-03":True,
        "2020-11-23":True,
        "2020-12-23":True}

    try:
        return holidays[day]
    except:
        return False
