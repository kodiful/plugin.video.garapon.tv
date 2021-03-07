# -*- coding: utf-8 -*-

import sys
import os
import shutil
import datetime

from urllib.parse import parse_qs

import xbmc

from resources.lib.common import Common
from resources.lib.browse import Browse
from resources.lib.channel import Channel
from resources.lib.genre import Genre
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
        for id in ['keyword', 'query']:
            settings[id] = Common.GET(id)
            Common.SET(id, '')
        for id in ['source']:
            settings[id] = Common.GET(id)
            Common.SET(id, '0')
        for id in ['channel']:
            settings[id] = Common.GET(id)
            Common.SET(id, Channel().getDefault())
        for id in ['g0', 'g00', 'g01', 'g02', 'g03', 'g04', 'g05', 'g06', 'g07', 'g08', 'g09', 'g10', 'g11']:
            settings[id] = Common.GET(id)
            Common.SET(id, Genre().getDefault(id))

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
        g0 = args.get('g0', '')
        g1 = args.get('g1', '')
        SmartList(settings).beginEdit(name, ch, g0, g1)
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
