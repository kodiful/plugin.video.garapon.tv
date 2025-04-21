# -*- coding: utf-8 -*-

import sys
import os
import shutil
import socket
from urllib.parse import parse_qs

import xbmc

from resources.lib.common import Common
from resources.lib.db import ThreadLocal, DB
from resources.lib.browse import Browse
from resources.lib.smartlist import Smartlist
from resources.lib.initialize import initializeNetwork
from resources.lib.initialize import initializeSession
from resources.lib.initialize import initializeChannel
from resources.lib.initialize import checkSettings


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

    # HTTP接続におけるタイムアウト(秒)
    socket.setdefaulttimeout(60)

    # DBインスタンスを作成
    ThreadLocal.db = DB()

    # パラメータ抽出
    args = parse_qs(sys.argv[2][1:], keep_blank_values=True)
    args = dict(map(lambda x: (x[0], x[1][0]), args.items()))

    # アドオン設定をコピー
    require_settings = False
    if os.path.isfile(Common.SETTINGS_FILE) is False:
        # settings.xmlがない場合は暫定的にテンプレートをコピーする
        require_settings = True
        shutil.copyfile(Common.TEMPLATE_FILE, Common.SETTINGS_FILE)

    # キャッシュサイズが未設定の場合は設定
    if Common.GET('cache') == '':
        Cache().update()

    # 各種処理
    action = args.get('action', '')
    if action == '':
        # 必須設定をチェック
        if checkSettings():
            # SETTINGS_FILEを作成
            if require_settings:
                initializeChannel()
            # トップ画面を開く
            Browse().top()
        else:
            # 未設定の場合はダイアログを開く
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    elif action == 'selectDate':
        Browse().select_date()

    elif action == 'selectChannel':
        Browse().select_channel()

    elif action == 'selectGenre':
        Browse().select_genre()

    elif action == 'selectSubgenre':
        Browse().select_subgenre()

    # play
    elif action == 'play':
        Browse().play(args.get('stream'))

    # search
    elif action == 'search':
        Browse().search()

    # onair
    elif action == 'searchOnAir':
        Browse().search(target='onair')

    # favorites
    elif action == 'searchFavorites':
        Browse().search(target='favorites')

    elif action == 'setFavorites':
        Browse().set_favorites()

    # smartlist
    elif action == 'searchSmartlist':
        Browse().search(target='smartlist')

    elif action == 'editSmartlist':
        Smartlist().edit()

    elif action == 'deleteSmartlist':
        Smartlist().delete()

    # settings
    elif action == 'initializeSettings':
        if Common.GET('garapon_auto') == 'true':
            if initializeNetwork():
                xbmc.executebuiltin('RunPlugin(%s?action=initializeSession)' % sys.argv[0])
            else:
                xbmc.executebuiltin('RunPlugin(%s?action=openSettings)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?action=initializeSession)' % sys.argv[0])

    elif action == 'initializeSession':
        if initializeSession():
            xbmc.executebuiltin('RunPlugin(%s?action=initializeChannel)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?action=openSettings)' % sys.argv[0])

    elif action == 'initializeChannel':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?action=openSettings)' % sys.argv[0])

    # update session only
    elif action == 'updateSession':
        if initializeSession() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?action=openSettings)' % sys.argv[0])

    # update channel only
    elif action == 'updateChannel':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?action=openSettings)' % sys.argv[0])

    # clear cache
    elif action == 'clearCache':
        Cache().clear()
        Cache().update()

    # open settings
    elif action == 'openSettings':
        # update cache settings
        Cache().update()
        # open settings
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    # unknown action
    else:
        Common.log('unknown action:', action)

    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
