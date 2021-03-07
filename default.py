# -*- coding: utf-8 -*-

import sys
import os
import shutil
import datetime

from urllib.parse import parse_qs

import xbmc

from resources.lib.common import Common
from resources.lib.browse import Browse
from resources.lib.smartlist import SmartList
from resources.lib.initialize import initializeNetwork
from resources.lib.initialize import initializeSession
from resources.lib.initialize import initializeChannel
from resources.lib.initialize import checkSettings

# HTTP接続におけるタイムアウト(秒)
import socket
socket.setdefaulttimeout(60)


class Cache():

    def __init__(self):
        self.files = os.listdir(Common.CACHE_PATH)

    def clear(self):
        for file in self.files:
            try:
                os.remove(os.path.join(Common.CACHE_PATH, file))
            except Exception:
                pass

    def update(self):
        size = 0
        for file in self.files:
            try:
                size = size + os.path.getsize(os.path.join(Common.CACHE_PATH, file))
            except Exception:
                pass
        if size > 1024 * 1024:
            Common.SET('cache', '%.1f MB / %d files' % (size / 1024 / 1024, len(self.files)))
        elif size > 1024:
            Common.SET('cache', '%.1f kB / %d files' % (size / 1024, len(self.files)))
        else:
            Common.SET('cache', '%d bytes / %d files' % (size, len(self.files)))


if __name__ == '__main__':

    # パラメータ抽出
    args = parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]

    mode = args.get('mode', '')
    url = args.get('url', '')

    # アドオン設定をコピー
    settings = {}
    if not os.path.isfile(Common.SETTINGS_FILE):
        # settings.xmlがない場合はテンプレートをコピーする
        shutil.copyfile(Common.TEMPLATE_FILE, Common.SETTINGS_FILE)
    else:
        for id in ['channel',
                   'genre0',
                   'genre00',
                   'genre01',
                   'genre02',
                   'genre03',
                   'genre04',
                   'genre05',
                   'genre06',
                   'genre07',
                   'genre08',
                   'genre09',
                   'genre10',
                   'genre11',
                   'keyword',
                   'query',
                   'source']:
            settings[id] = Common.GET(id)
            # コピーした後にリセット
            Common.SET(id, '0' if id == 'source' else '')

    # キャッシュサイズが未設定の場合は設定
    if Common.GET('cache') == '':
        Cache().update()

    # 各種処理
    if mode == '':
        # 必須設定をチェック
        if checkSettings():
            # 設定済であればトップ画面を開く
            Browse().top()
        else:
            # 未設定の場合はダイアログを開く
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    elif mode == 'selectDate':
        Browse(url).select_date()

    elif mode == 'selectChannel':
        Browse(url).select_channel()

    elif mode == 'selectGenre':
        Browse(url).select_genre()

    elif mode == 'selectSubgenre':
        Browse(url).select_subgenre()

    # search
    elif mode == 'search':
        Browse(url).search()

    # search onair
    elif mode == 'searchOnAir':
        Browse('%s&dt=e&sdate=%s' % (url, datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))).search(onair=True)

    # switch favorites
    elif mode == 'switchFavorites':
        Browse(url).favorites()

    # smartlist
    elif mode == 'beginEditSmartList':
        name = args.get('name')
        ch = args.get('ch', '')
        genre0 = args.get('genre0', '')
        genre1 = args.get('genre1', '')
        SmartList(settings).beginEdit(name, ch, genre0, genre1)
        # update cache settings
        Cache().update()
        # open settings & focus smartlist category
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        xbmc.executebuiltin('SetFocus(-98)')

    elif mode == 'endEditSmartList':
        SmartList(settings).endEdit()
        # refresh top page
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    elif mode == 'deleteSmartList':
        name = args.get('name')
        SmartList(settings).delete(name)
        # refresh top page
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    # settings
    elif mode == 'initializeSettings':
        if Common.GET('garapon_auto') == 'true':
            if initializeNetwork():
                xbmc.executebuiltin('RunPlugin(%s?mode=initializeSession)' % sys.argv[0])
            else:
                xbmc.executebuiltin('RunPlugin(%s?mode=openSettings)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=initializeSession)' % sys.argv[0])

    elif mode == 'initializeSession':
        if initializeSession():
            xbmc.executebuiltin('RunPlugin(%s?mode=initializeChannel)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=openSettings)' % sys.argv[0])

    elif mode == 'initializeChannel':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=openSettings)' % sys.argv[0])

    # update session only
    elif mode == 'updateSession':
        if initializeSession() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=openSettings)' % sys.argv[0])

    # update channel only
    elif mode == 'updateChannel':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=openSettings)' % sys.argv[0])

    # clear cache
    elif mode == 'clearCache':
        Cache().clear()
        Cache().update()

    # open settings
    elif mode == 'openSettings':
        # update cache settings
        Cache().update()
        # open settings
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
