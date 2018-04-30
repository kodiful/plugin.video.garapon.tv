# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import urlparse
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from resources.lib.common     import log
from resources.lib.const      import Const
from resources.lib.browse     import Browse
from resources.lib.item       import Cache
from resources.lib.smartlist  import SmartList
from resources.lib.initialize import initializeNetwork,initializeSession,initializeChannel,checkSettings,syncSession

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    for key in args.keys(): args[key] = args[key][0]
    mode = args.get('mode', '')
    url  = args.get('url',  '') # str
    name = args.get('name', '').decode('utf-8') # unicode
    # ログ
    log([mode,url,name])
    # 必須項目が設定されていない場合はダイアログを開く
    if mode == '' and checkSettings() is False:
        xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])
        return
    # キャッシュサイズが未設定の場合は設定
    if Const.GET('cache') == '': Cache().update()

    # 各種処理
    if mode=='':
        Browse().show('top')

    # browse
    elif mode=='11':
        Browse(url).show('date')

    elif mode=='12':
        Browse(url).show('channel')

    elif mode=='13':
        Browse(url).show('genre')

    elif mode=='14':
        Browse(url).show('subgenre')

    # search
    elif mode=='15':
        Browse(url).search()

    # search onair
    elif mode=='16':
        Browse('%s&dt=e&sdate=%s' % (url,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))).search(onair=True)

    # manage favorites
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
        xbmc.executebuiltin('Container.Update(%s)' % sys.argv[0])

    elif mode=='63':
        SmartList().edit(name)
        # open settings
        xbmc.executebuiltin('RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='64':
        SmartList().delete(name)
        # refresh top page
        xbmc.executebuiltin('Container.Update(%s)' % sys.argv[0])

    # settings
    elif mode=='70':
        if Const.GET('garapon_auto') == 'true':
            if initializeNetwork():
                xbmc.executebuiltin('RunPlugin(%s?mode=71,replace)' % sys.argv[0])
            else:
                xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=71,replace)' % sys.argv[0])

    elif mode=='71':
        if initializeSession():
            xbmc.executebuiltin('RunPlugin(%s?mode=72,replace)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    elif mode=='72':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # update session only
    elif mode=='73':
        if initializeSession() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # update channel only
    elif mode=='74':
        if initializeChannel() and checkSettings():
            xbmc.executebuiltin('Container.Update(%s)' % sys.argv[0])
        else:
            xbmc.executebuiltin('RunPlugin(%s?mode=82)' % sys.argv[0])

    # cache
    elif mode=='80':
        Cache().clear()
        Cache().update()

    # settings
    elif mode=='82':
        # clear smartlist
        SmartList().clear()
        # update cache settings
        Cache().update()
        # open settings
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)

    elif mode=='83':
        # update cache settings
        Cache().update()
        # open settings & focus smartlist category
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
        xbmc.executebuiltin('SetFocus(102)') # smartlist category which is the 3rd
        xbmc.executebuiltin('SetFocus(215)') # keyword control which is the 16th including hidden controls

    elif mode=='84':
        # sync gtvsession
        syncSession(url);

    elif mode=='85':
        # add to smartlist
        SmartList().set(name, url)
        SmartList().add()

if __name__  == '__main__': main()
