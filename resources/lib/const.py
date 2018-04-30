# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import xbmc, xbmcaddon

class Const:

    # 開発者ID
    DEV_ID = '64ee928bac3e56e810a613bd350e0275'

    # ページあたりの最大表示項目数
    ITEMS = 100

    # ガラポンTVクライアント
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')

    STR = ADDON.getLocalizedString
    GET = ADDON.getSetting
    SET = ADDON.setSetting

    # ガラポンTVクライアント機能拡張
    PLUS_ADDON_ID = 'plugin.video.garapon.tv.plus'
    try:
        PLUS_ADDON = xbmcaddon.Addon(PLUS_ADDON_ID)
        DOWNLOAD_PATH = PLUS_ADDON.getSetting('download_path')
    except:
        PLUS_ADDON = None
        DOWNLOAD_PATH = None

    # ディレクトリパス
    PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile').decode('utf-8'))
    PLUGIN_PATH = xbmc.translatePath(ADDON.getAddonInfo('path').decode('utf-8'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'image')

    # キャッシュパス
    CACHE_PATH = os.path.join(PROFILE_PATH, 'cache')
    if not os.path.isdir(CACHE_PATH): os.makedirs(CACHE_PATH)

    # データベース
    DB_PATH = xbmc.translatePath('special://database')
    CACHE_DB = os.path.join(DB_PATH, 'Textures13.db')

    # ファイルパス
    SETTINGS_FILE    = os.path.join(RESOURCES_PATH, 'settings.xml')
    TEMPLATE_FILE    = os.path.join(DATA_PATH, 'settings.xml')
    GENRE_FILE       = os.path.join(DATA_PATH, 'genre.js')
    CHANNEL_FILE     = os.path.join(PROFILE_PATH, 'channel.js')
    SMARTLIST_FILE   = os.path.join(PROFILE_PATH, 'smartlist.js')
    RESUME_FILE      = os.path.join(PROFILE_PATH, 'resume.js')

    # サムネイル
    RETRO_TV         = os.path.join(IMAGE_PATH, 'icons8-retro-tv-filled-500.png')
    CALENDAR         = os.path.join(IMAGE_PATH, 'icons8-calendar-filled-500.png')
    RADIO_TOWER      = os.path.join(IMAGE_PATH, 'icons8-radio-tower-filled-500.png')
    CATEGORIZE       = os.path.join(IMAGE_PATH, 'icons8-categorize-filled-500.png')
    FAVORITE_FOLDER  = os.path.join(IMAGE_PATH, 'icons8-favorite-folder-filled-500.png')
    DOWNLOADS_FOLDER = os.path.join(IMAGE_PATH, 'icons8-downloads-folder-filled-500.png')
    BROWSE_FOLDER    = os.path.join(IMAGE_PATH, 'icons8-browse-folder-filled-500.png')
    RIGHT            = os.path.join(IMAGE_PATH, 'icons8-right-filled-500.png')
