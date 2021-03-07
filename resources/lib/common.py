# -*- coding: utf-8 -*-

import os

from resources.lib.commonmethods import Common as C


class Common(C):

    # 開発者ID
    DEV_ID = '64ee928bac3e56e810a613bd350e0275'

    # ページあたりの最大表示項目数
    ITEMS = 100

    # ディレクトリパス
    RESOURCES_PATH = os.path.join(C.PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'image')

    # キャッシュパス
    CACHE_PATH = os.path.join(C.PROFILE_PATH, 'cache')
    if not os.path.isdir(CACHE_PATH):
        os.makedirs(CACHE_PATH)

    # データベース
    CACHE_DB = os.path.join(C.DB_PATH, 'Textures13.db')

    # ファイルパス
    SETTINGS_FILE = os.path.join(RESOURCES_PATH, 'settings.xml')
    TEMPLATE_FILE = os.path.join(DATA_PATH, 'settings.xml')
    GENRE_FILE = os.path.join(DATA_PATH, 'genre.js')
    CHANNEL_FILE = os.path.join(C.PROFILE_PATH, 'channel.js')
    SMARTLIST_FILE = os.path.join(C.PROFILE_PATH, 'smartlist.js')
    RESUME_FILE = os.path.join(C.PROFILE_PATH, 'resume.js')

    # サムネイル
    RETRO_TV = os.path.join(IMAGE_PATH, 'icons8-retro-tv-filled-500.png')
    CALENDAR = os.path.join(IMAGE_PATH, 'icons8-calendar-filled-500.png')
    RADIO_TOWER = os.path.join(IMAGE_PATH, 'icons8-radio-tower-filled-500.png')
    CATEGORIZE = os.path.join(IMAGE_PATH, 'icons8-categorize-filled-500.png')
    FAVORITE_FOLDER = os.path.join(IMAGE_PATH, 'icons8-favorite-folder-filled-500.png')
    DOWNLOADS_FOLDER = os.path.join(IMAGE_PATH, 'icons8-downloads-folder-filled-500.png')
    BROWSE_FOLDER = os.path.join(IMAGE_PATH, 'icons8-browse-folder-filled-500.png')
    RIGHT = os.path.join(IMAGE_PATH, 'icons8-right-filled-500.png')
