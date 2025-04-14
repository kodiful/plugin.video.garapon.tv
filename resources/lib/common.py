# -*- coding: utf-8 -*-

import os
import json
import inspect
import traceback
import calendar
import urllib.request
import urllib.error
from datetime import datetime

import chardet
# add the following line to the <requires> section of addon.xml
# <import addon="script.module.chardet" version="3.0.4"/>

import xbmc
import xbmcaddon
import xbmcvfs


class Common:

    # アドオンオブジェクト
    ADDON = xbmcaddon.Addon()

    # アドオン属性
    INFO = ADDON.getAddonInfo
    ADDON_ID = INFO('id')
    ADDON_NAME = INFO('name')
    PROFILE_PATH = xbmcvfs.translatePath(INFO('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(INFO('path'))
    DB_PATH = xbmcvfs.translatePath('special://database')

    # アドオン設定へのアクセス
    STR = ADDON.getLocalizedString
    GET = ADDON.getSetting
    SET = ADDON.setSetting
    
    # 開発者ID
    DEV_ID = '64ee928bac3e56e810a613bd350e0275'

    # ページあたりの最大表示項目数
    ITEMS = 100

    # ディレクトリパス
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'icons')

    # キャッシュパス
    CACHE_PATH = os.path.join(PROFILE_PATH, 'cache')
    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    # データベース
    CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')

    # ファイルパス
    SETTINGS_FILE = os.path.join(RESOURCES_PATH, 'settings.xml')
    ORIGINAL_SETTINGS = os.path.join(DATA_PATH, 'settings', 'settings.xml')
    SMARTLIST_SETTINGS = os.path.join(DATA_PATH, 'settings', 'smartlist.xml')
    TEMPLATE_FILE = os.path.join(DATA_PATH, 'templates', 'settings.xml')
    GENRE_FILE = os.path.join(DATA_PATH, 'genre.js')
    CHANNEL_FILE = os.path.join(PROFILE_PATH, 'channel.js')
    SMARTLIST_FILE = os.path.join(PROFILE_PATH, 'smartlist.js')
    RESUME_FILE = os.path.join(PROFILE_PATH, 'resume.js')

    # サムネイル
    RETRO_TV = os.path.join(IMAGE_PATH, 'tv.png')
    CALENDAR = os.path.join(IMAGE_PATH, 'calendar.png')
    RADIO_TOWER = os.path.join(IMAGE_PATH, 'satellite.png')
    CATEGORIZE = os.path.join(IMAGE_PATH, 'tag.png')
    FAVORITE_FOLDER = os.path.join(IMAGE_PATH, 'favourite.png')
    DOWNLOADS_FOLDER = os.path.join(IMAGE_PATH, 'folder.png')
    BROWSE_FOLDER = os.path.join(IMAGE_PATH, 'set.png')
    RIGHT = os.path.join(IMAGE_PATH, 'play.png')

    # ファイル読み込み
    @staticmethod
    def read_file(filepath, encoding=None):
        if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
            try:
                with open(filepath, 'rb') as f:
                    data = f.read()
                return data.decode(encoding=encoding or chardet.detect(data)['encoding'], errors='ignore')
            except Exception as e:
                Common.log(filepath, str(e), error=True)
                return None
        else:
            return None

    # ファイル書き出し
    @staticmethod
    def write_file(filepath, data):
        try:
            if isinstance(data, bytes):
                with open(filepath, 'wb') as f:
                    f.write(data)
            elif isinstance(data, str):
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(data)
            else:
                raise TypeError
        except Exception as e:
            Common.log(filepath, str(e), error=True)

    # JSONデータ読み込み
    @staticmethod
    def read_json(filepath):
        data = Common.read_file(filepath)
        if data:
            try:
                return json.loads(data)
            except Exception as e:
                Common.log(filepath, str(e), error=True)
                return None
        else:
            return None

    # JSONデータ書き出し
    @staticmethod
    def write_json(filepath, data):
        try:
            Common.write_file(filepath, json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4))
        except Exception as e:
            Common.log(filepath, str(e), error=True)

    # URLから読み込み
    @staticmethod
    def read_url(url, headers={}):
        opener = urllib.request.build_opener()
        h = [('User-Agent', 'Mozilla/5.0')]  # User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
        for key, val in headers.items():
            h.append((key, val))
        opener.addheaders = h
        try:
            response = opener.open(url)
            buf = response.read()
            response.close()
        except urllib.error.HTTPError as e:
            Common.log('HTTPError url:{url}, code:{code}'.format(url=url, code=e.code), error=True)
            buf = ''
        except urllib.error.URLError as e:
            Common.log('URLError url:{url}, reason:{reason}'.format(url=url, reason=e.reason), error=True)
            buf = ''
        except Exception as e:
            Common.log(url, str(e), error=True)
            buf = ''
        return buf

    # 通知
    @staticmethod
    def notify(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        name = addon.getAddonInfo('name')
        # デフォルト設定
        if options.get('error'):
            image = 'DefaultIconError.png'
            level = xbmc.LOGERROR
        else:
            image = 'DefaultIconInfo.png'
            level = xbmc.LOGINFO
        # ポップアップする時間
        duration = options.get('duration', 10000)
        # ポップアップアイコン
        image = options.get('image', image)
        # メッセージ
        messages = ' '.join(map(lambda x: str(x), messages))
        # ポップアップ通知
        xbmc.executebuiltin(f'Notification("{name}","{messages}",{duration},"{image}")')
        # ログ出力
        Common.log(messages, level=level)

    # ログ
    @staticmethod
    def log(*messages, **options):
        # アドオン
        addon = xbmcaddon.Addon()
        # ログレベル、メッセージを設定
        if isinstance(messages[0], Exception):
            level = options.get('level', xbmc.LOGERROR)
            message = '\n'.join(list(map(lambda x: x.strip(), traceback.TracebackException.from_exception(messages[0]).format())))
            if len(messages[1:]) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages[1:]))
        else:
            level = options.get('level', xbmc.LOGINFO)
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            name = frame.f_code.co_name
            id = addon.getAddonInfo('id')
            message = f'Addon "{id}", File "{filename}", line {lineno}, in {name}'
            if len(messages) > 0:
                message += ': ' + ' '.join(map(lambda x: str(x), messages))
        # ログ出力
        xbmc.log(message, level)

    @staticmethod
    def datetime(datetimestr):
        # 2023-04-20 05:00:00 -> datetime(2023, 4, 20, 5, 0, 0)
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, time = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        h, m, s = map(int, time.split(':'))
        return datetime(year, month, day, h, m, s)

    @staticmethod
    def weekday(datetimestr):
        # 2023-04-20 05:00:00 -> calendar.weekday(2023, 4, 20) -> 3
        datetimestr = datetimestr + '1970-01-01 00:00:00'[len(datetimestr):]  # padding
        date, _ = datetimestr.split(' ')
        year, month, day = map(int, date.split('-'))
        return calendar.weekday(year, month, day)

    # workaround for encode problems for strftime on Windows
    # cf. https://ja.stackoverflow.com/questions/44597/windows上のpythonのdatetime-strftimeで日本語を使うとエラーになる
    @staticmethod
    def strftime(d, format):
        return d.strftime(format.encode('unicode-escape').decode()).encode().decode('unicode-escape')
