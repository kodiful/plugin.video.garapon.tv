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
    CONTENTS_DB = os.path.join(PROFILE_PATH, 'contents.db')
    TEMPLATE_DB = os.path.join(DATA_PATH, 'templates', 'contents.db')
    CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')

    # ファイルパス
    SETTINGS_FILE = os.path.join(RESOURCES_PATH, 'settings.xml')
    ORIGINAL_SETTINGS = os.path.join(DATA_PATH, 'settings', 'settings.xml')
    SMARTLIST_SETTINGS = os.path.join(DATA_PATH, 'settings', 'smartlist.xml')
    TEMPLATE_FILE = os.path.join(DATA_PATH, 'templates', 'settings.xml')

    # サムネイル
    RETRO_TV = os.path.join(IMAGE_PATH, 'tv.png')
    CALENDAR = os.path.join(IMAGE_PATH, 'calendar.png')
    RADIO_TOWER = os.path.join(IMAGE_PATH, 'satellite.png')
    CATEGORIZE = os.path.join(IMAGE_PATH, 'tag.png')
    FAVORITE_FOLDER = os.path.join(IMAGE_PATH, 'favourite.png')
    DOWNLOADS_FOLDER = os.path.join(IMAGE_PATH, 'folder.png')
    BROWSE_FOLDER = os.path.join(IMAGE_PATH, 'set.png')
    RIGHT = os.path.join(IMAGE_PATH, 'play.png')

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
