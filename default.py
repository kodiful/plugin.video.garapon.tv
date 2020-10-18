# -*- coding: utf-8 -*-

import sys
import os
import shutil
import datetime
import urlparse
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from resources.lib.common     import log
from resources.lib.const      import Const
from resources.lib.browse     import Browse
from resources.lib.smartlist  import SmartList
from resources.lib.initialize import *

# HTTP接続におけるタイムアウト(秒)
import socket
socket.setdefaulttimeout(60)


class Cache():

    def __init__(self):
        self.files = os.listdir(Const.CACHE_PATH)

    def clear(self):
        for file in self.files:
            try: os.remove(os.path.join(Const.CACHE_PATH, file))
            except: pass

    def update(self):
        size = 0
        for file in self.files:
            try: size = size + os.path.getsize(os.path.join(Const.CACHE_PATH, file))
            except: pass
        if size > 1024*1024:
            Const.SET('cache', '%.1f MB / %d files' % (size/1024.0/1024.0,len(self.files)))
        elif size > 1024:
            Const.SET('cache', '%.1f kB / %d files' % (size/1024.0,len(self.files)))
        else:
            Const.SET('cache', '%d bytes / %d files' % (size,len(self.files)))


if __name__  == '__main__':

    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys(): args[key] = args[key][0]

    mode = args.get('mode', '')
    url  = args.get('url',  '')
    name = args.get('name', '')

    # settings.xmlがない場合はテンプレートをコピーする
    if not os.path.isfile(Const.SETTINGS_FILE):
        shutil.copyfile(Const.TEMPLATE_FILE, Const.SETTINGS_FILE)

    # キャッシュサイズが未設定の場合は設定
    if Const.GET('cache') == '':
        Cache().update()

    # 各種処理
    if mode=='':
        # 必須設定をチェック
        if checkSettings():
            # 設定済であればトップ画面を開く
            Browse().top()
        else:
            # 未設定の場合はダイアログを開く
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)

    elif mode=='11':
        Browse(url).select_date()

    elif mode=='12':
        Browse(url).select_channel()

    elif mode=='13':
        Browse(url).select_genre()

    elif mode=='14':
        Browse(url).select_subgenre()

    # search
    elif mode=='15':
        Browse(url).search()

    # search onair
    elif mode=='16':
        Browse('%s&dt=e&sdate=%s' % (url,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))).search(onair=True)

    # switch favorites
    elif mode=='20':
        Browse(url).favorites()

    # smartlist
    elif mode=='60':
        SmartList().clear()
        # open settings
        xbmc.executebuiltin('RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='61':
        SmartList().set(name, url)
        # open settings
        xbmc.executebuiltin('RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='62':
        SmartList().add()
        # refresh top page
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    elif mode=='63':
        SmartList().edit(name)
        # open settings
        xbmc.executebuiltin('RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='64':
        SmartList().delete(name)
        # refresh top page
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    # settings
    elif mode=='70':
        if Const.GET('garapon_auto') == 'true':
            if initializeNetwork():
                xbmc.executebuiltin('RunPlugin(%s?mode=71)' % sys.argv[0])
            else:
                xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=71)' % sys.argv[0])

    elif mode=='71':
        if initializeSession():
            xbmc.executebuiltin('RunPlugin(%s?mode=72)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    elif mode=='72':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # update session only
    elif mode=='73':
        if initializeSession() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # update channel only
    elif mode=='74':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # clear cache
    elif mode=='80':
        Cache().clear()
        Cache().update()

    # open settings
    elif mode=='82':
        # clear smartlist
        SmartList().clear()
        # update cache settings
        Cache().update()
        # open settings
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)

    # open settings as smartlist editor
    elif mode=='83':
        # update cache settings
        Cache().update()
        # open settings & focus smartlist category
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
        xbmc.executebuiltin('SetFocus(102)') # smartlist category which is the 3rd
        xbmc.executebuiltin('SetFocus(215)') # keyword control which is the 16th including hidden controls

    elif mode=='85':
        # add to smartlist
        SmartList().set(name, url)
        SmartList().add()
