# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import urllib, urllib2
import math
import hashlib
import datetime, time
import re
import os
import codecs
import threading
import json
import xbmcplugin
import xbmcgui
import xbmcaddon

from urllib2 import URLError, HTTPError

from resources.lib.common    import(addon,garapon,radiruko,settings)
from resources.lib.common    import(SETTINGS_FILE,TEMPLATE_FILE)
from resources.lib.common    import(RESUME_FILE)
from resources.lib.common    import(isholiday,addon_error,addon_debug,notify)

from resources.lib.item      import(Item,Cache,query2desc)
from resources.lib.channel   import(Channel)
from resources.lib.genre     import(Genre)
from resources.lib.smartlist import(SmartList)

nextAired = 0

def initializeNetwork():
    # リセット
    addon.setSetting('garapon_addr', '')
    addon.setSetting('garapon_http', '')
    addon.setSetting('garapon_rtmp', '')
    # データ取得
    garapon_id = addon.getSetting('garapon_id')
    garapon_pw = addon.getSetting('garapon_pw')
    url = 'http://garagw.garapon.info/getgtvaddress'
    query = 'dev_id=' + settings['dev_id']
    query += '&user=' + garapon_id
    query += '&md5passwd=' + hashlib.md5(garapon_pw).hexdigest()
    request_body = query
    req = urllib2.Request(url, request_body)
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('initializeNetwork: HTTPError: %s' % str(e.code))
        return 'Network initialization failed'
    except URLError, e:
        addon_error('initializeNetwork: URLError: %s' % str(e.reason))
        return 'Network initialization failed'
    response_body = response.read()
    response.close()
    params = {}
    for i in response_body.split('\n'):
        try:
            (key, value) = i.split(';', 1)
            if key == '0':
                params['message'] = value
            elif key == '1':
                params['message'] = value
            else:
                params[key] = value
        except:
            pass
    if params['message'] == 'success':
        addon.setSetting('garapon_addr', params['ipaddr'])
        if params['ipaddr'] == params['gipaddr']:
            addon.setSetting('garapon_http', params['port'])
            addon.setSetting('garapon_rtmp', params['port2'])
        else:
            addon.setSetting('garapon_http', '')
            addon.setSetting('garapon_rtmp', '')
        message = 'success'
    else:
        addon_error('initializeNetwork: status: %s' % params['message'])
        message = 'Network initialization failed'
    return message


def initializeSession():
    # リセット
    addon.setSetting('garapon_session', '')
    # データ取得
    garapon_addr = addon.getSetting('garapon_addr')
    garapon_http = addon.getSetting('garapon_http')
    garapon_rtmp = addon.getSetting('garapon_rtmp')
    garapon_id = addon.getSetting('garapon_id')
    garapon_pw = addon.getSetting('garapon_pw')
    url = 'http://' + garapon_addr
    if garapon_http:
        url += ':' + garapon_http
    url += '/gapi/v3/auth?dev_id=' + settings['dev_id']
    request_body = 'type=login' + '&loginid=' + garapon_id + '&password=' + garapon_pw
    req = urllib2.Request(url, request_body)
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('initializeSession: HTTPError: %s' % str(e.code))
        return 'Session initialization failed'
    except URLError, e:
        addon_error('initializeSession: URLError: %s' % str(e.reason))
        return 'Session initialization failed'
    response_body = response.read()
    response.close()
    response_data = json.loads(response_body)
    if response_data['status'] == 1:
        if response_data['login'] == 1:
            gtvsession = response_data['gtvsession']
            addon.setSetting('garapon_session', gtvsession)
            addon.setSetting('garapon_authtime', str(time.time()))
            message = 'success'
        else:
            addon_error('initializeSession: login: %s' % str(response_data['login']))
            message = 'Session initialization failed'
    else:
        addon_error('initializeSession: status: %s' % str(response_data['status']))
        message = 'Session initialization failed'
    return message


def initializeChannel():
    # リセット
    addon.setSetting('garapon_ch', '')
    # データ取得
    garapon_addr = addon.getSetting('garapon_addr')
    garapon_http = addon.getSetting('garapon_http')
    garapon_rtmp = addon.getSetting('garapon_rtmp')
    gtvsession = addon.getSetting('garapon_session')
    url = 'http://' + garapon_addr
    if garapon_http:
        url += ':' + garapon_http
    url += '/gapi/v3/channel?dev_id=' + settings['dev_id'] + '&gtvsession=' + gtvsession
    req = urllib2.Request(url, '')
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('initializeChannel: HTTPError: %s' % str(e.code))
        return 'Channel initialization failed'
    except URLError, e:
        addon_error('initializeChannel: URLError: %s' % str(e.reason))
        return 'Channel initialization failed'
    response_body = response.read()
    response.close()
    response_data = json.loads(response_body)
    if response_data['status'] == 1:
        # ファイルに書き出す
        Channel().setData(response_data)
        # チャンネル数を設定
        addon.setSetting('garapon_ch', '%d channels' % len(response_data['ch_list'].keys()))
        # テンプレートからsettings.xmlを生成
        data = Genre().getLabel() # genre
        data['channel'] = Channel().getLabel() # channel
        f = codecs.open(TEMPLATE_FILE,'r','utf-8')
        template = f.read()
        f.close()
        source = template.format(
            channel=data['channel'],
            genre0=data['genre0'],
            genre00=data['genre00'],
            genre01=data['genre01'],
            genre02=data['genre02'],
            genre03=data['genre03'],
            genre04=data['genre04'],
            genre05=data['genre05'],
            genre06=data['genre06'],
            genre07=data['genre07'],
            genre08=data['genre08'],
            genre09=data['genre09'],
            genre10=data['genre10'],
            genre11=data['genre11'])
        f = codecs.open(SETTINGS_FILE,'w','utf-8')
        f.write(source)
        f.close()
        # 完了
        message = 'success'
    else:
        addon_error('initializeChannel: status: %s' % str(response_data['status']))
        message = 'Channel initialization failed'
    return message


def setupSettings():
    # ステータス
    status = True
    # 設定を格納
    settings['addr'] = addon.getSetting('garapon_addr')
    settings['http'] = addon.getSetting('garapon_http')
    settings['rtmp'] = addon.getSetting('garapon_rtmp')
    settings['session'] = addon.getSetting('garapon_session')
    settings['authtime'] = addon.getSetting('garapon_authtime')
    #settings['protocol'] = addon.getSetting('protocol')
    #settings['thumb'] = addon.getSetting('thumb')
    #settings['favorite'] = addon.getSetting('favorite')
    #settings['download'] = addon.getSetting('download')
    #settings['ffmpeg'] = addon.getSetting('ffmpeg')
    settings['protocol'] = 'HLS'
    settings['thumb'] = 'Fit'
    settings['favorite'] = 'true'
    settings['download'] = 'false'
    settings['ffmpeg'] = ''

    # 必須設定項目をチェック
    if addon.getSetting('garapon_id') == '':
        status = False
    if addon.getSetting('garapon_pw') == '':
        status = False
    if settings['addr'] == '':
        status = False
    if settings['session'] == '':
        status = False
    # ステータスを返す
    return status


def searchGaraponTV(squery, onair=False, retry=True): # type(squery)=str, type(retry)=boolean
    # 検索
    url = 'http://' + settings['addr']
    if settings['http']:
        url += ':' + settings['http']
    url += '/gapi/v3/search?dev_id=' + settings['dev_id'] + '&gtvsession=' + settings['session']
    req = urllib2.Request(url, squery)
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('searchGaraponTV: HTTPError: %s' % str(e.code))
        return 'Search failed'
    except URLError, e:
        addon_error('searchGaraponTV: URLError: %s' % str(e.reason))
        return 'Search failed'
    response_body = response.read()
    response.close()
    # 検索結果
    response_data = json.loads(response_body)
    if response_data['status'] == 1:
        # 検索結果の番組
        programs = response_data['program']
        if onair:
            # 放送中の番組はチャンネル順
            for item in sorted(programs, key=lambda item: item['ch']):
                if item['ts'] == 1: addItem(item, onair)
            # 放送中の番組の終了時刻を計算
            global nextAired
            nextAired = checkOnAir(programs)
        else:
            # 放送済みの番組は時間降順
            for item in sorted(programs, key=lambda item: item['startdate'], reverse=True):
                if item['ts'] == 1: addItem(item, onair)
        # 検索結果の続きがある場合は次のページへのリンクを表示
        hit = int(response_data['hit'])
        page = int(re.search('&p=([0-9]+)',squery).group(1))
        if hit > page*settings['apage']:
            squery = re.sub('&p=([0-9]+)','&p='+str(page+1),squery)
            #全{totalpages}ページ({hit}番組)のうち{page}ページ目を表示します
            description = addon.getLocalizedString(30921).format(
                totalpages=int(math.ceil(1.0*hit/settings['apage'])),
                hit=hit,
                page=page+1) + '\n'
            #次のページへ
            addDir('[COLOR green]%s[/COLOR]' % (addon.getLocalizedString(30922)),squery,15,description,thumbnail='DefaultProgram.png')
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return 'success'
    elif retry == True:
        result = initializeSession()
        if result == 'success':
            if setupSettings():
                return searchGaraponTV(squery, onair, retry=False)
            else:
                addon_error('searchGaraponTV: setupSettings failed')
                return 'Search failed'
        else:
            addon_error('searchGaraponTV: initializeSession failed')
            return 'Search failed'
    else:
        addon_error('searchGaraponTV: retry: %s' % str(retry))
        return 'Search failed'


def browseGaraponTV(umode, squery=''): # type(umode)=unicode, type(squery)= str

    if squery == '': squery = 'n=%d&p=1&video=all' % (settings['apage'])
    description = query2desc(squery)

    if umode == 'top':
        #放送中:テレビ
        addDir(addon.getLocalizedString(30916),squery,16,addon.getLocalizedString(30917),showcontext='top',thumbnail='DefaultTVShows.png')
        #放送中:ラジオ
        if radiruko:
            addDir(addon.getLocalizedString(30931),'',81,addon.getLocalizedString(30932),showcontext='top',thumbnail='DefaultTVShows.png')
        #検索:日付
        addDir(addon.getLocalizedString(30933),'',11,addon.getLocalizedString(30918),showcontext='top',thumbnail='DefaultProgram.png')
        #検索:チャンネル
        addDir(addon.getLocalizedString(30934),'',12,addon.getLocalizedString(30918),showcontext='top',thumbnail='DefaultProgram.png')
        #検索:ジャンル
        addDir(addon.getLocalizedString(30935),'',13,addon.getLocalizedString(30918),showcontext='top',thumbnail='DefaultProgram.png')
        #コレクション:お気に入り
        if settings['favorite'] == 'true':
            addDir(addon.getLocalizedString(30923),squery+'&rank=all',15,addon.getLocalizedString(30924),showcontext='top',thumbnail='DefaultProgram.png')
        #コレクション:ダウンロード
        if settings['download'] == 'true':
            addDir(addon.getLocalizedString(30927),'',17,addon.getLocalizedString(30928),showcontext='top',thumbnail='DefaultProgram.png')
        #スマートリスト
        for i in SmartList().getList():
            title = i['title']
            query = i['query']
            addDir(title,query,15,query2desc(query),showcontext='smartlist',thumbnail='DefaultVideoPlaylists.png')
    elif umode == 'date':
        #すべての日付
        name = '[COLOR green]'+addon.getLocalizedString(30912)+'[/COLOR]'
        if squery.find('&ch=') == -1:
            mode = 12
        elif squery.find('&genre0=') == -1:
            mode = 13
        else:
            mode = 15
        addDir(name,squery+'&sdate=&edate=',mode,description,thumbnail='DefaultProgram.png')
        #月,火,水,木,金,土,日
        w = addon.getLocalizedString(30920).split(',')
        for i in range(120):
            d = datetime.date.today() - datetime.timedelta(i)
            wd = d.weekday()
            #月日
            date1 = d.strftime(addon.getLocalizedString(30919).encode('utf-8','ignore')).decode('utf-8')  + '(' + w[wd]+ ')'
            date2 = d.strftime('%Y-%m-%d')
            if isholiday(date2) or wd == 6:
                name = '[COLOR red]' + date1 + '[/COLOR]'
            elif wd == 5:
                name = '[COLOR blue]' + date1 + '[/COLOR]'
            else:
                name = date1
            query = '%s&sdate=%s 00:00:00&edate=%s 23:59:59' % (squery,date2,date2)
            if squery.find('&ch=') == -1:
                mode = 12
            elif squery.find('&genre0=') == -1:
                mode = 13
            else:
                mode = 15
            addDir(name,query,mode,description,thumbnail='DefaultProgram.png')
    elif umode == 'channel':
        for ch in Channel().getList():
            name = ch['name']
            id = ch['id']
            query = squery+'&ch='+id
            if squery.find('&genre0=') == -1:
                mode = 13
            elif squery.find('&sdate=') == -1:
                mode = 11
            else:
                mode = 15
            addDir(name,query,mode,description,thumbnail='DefaultProgram.png')
    elif umode == 'genre':
        for i in Genre().getList():
            name = i['name']
            id = i['id']
            if id == '':
                if squery.find('&ch=') == -1:
                    mode = 12
                elif squery.find('&sdate=') == -1:
                    mode = 11
                else:
                    mode = 15
                addDir(name,squery+'&genre0=&genre1=',mode,description,thumbnail='DefaultProgram.png')
            else:
                addDir(name,squery+'&genre0='+id,14,description,thumbnail='DefaultProgram.png')
    elif umode == 'subgenre':
        genre0 = re.search('&genre0=([0-9]+)',squery).group(1)
        for i in Genre().getList(genre0):
            name = i['name']
            id = i['id']
            if squery.find('&ch=') == -1:
                mode = 12
            elif squery.find('&sdate=') == -1:
                mode = 11
            else:
                mode = 15
            addDir(name,squery+'&genre1='+id,mode,description,thumbnail='DefaultProgram.png')
    # end of directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def manageFavorites(squery):
    url = 'http://' + settings['addr']
    if settings['http']:
        url += ':' + settings['http']
    url += '/gapi/v3/favorite?dev_id=' + settings['dev_id'] + '&gtvsession=' + settings['session']
    req = urllib2.Request(url, squery)
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('manageFavorites: HTTPError: %s' % str(e.code))
        return 'Operation failed'
    except URLError, e:
        addon_error('manageFavorites: URLError: %s' % str(e.reason))
        return 'Operation failed'
    response_body = response.read()
    response.close()
    response_data = json.loads(response_body)
    if response_data['status'] == 1:
        message = 'success'
    else:
        addon_error('manageFavorites: status: %s' % str(response_data['status']))
        message = 'Operation failed'
    return message


def browseDownloads():
    list = Downloads().getList()
    if len(list) > 0:
        squery = 'n=%d&p=1&video=all&gtvidlist=%s' % (settings['apage'], ','.join(list))
        searchGaraponTV(squery, onair=False, retry=True)
    else:
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


def addDir(name, url, mode, description, showcontext='', thumbnail='DefaultFolder.png'):
    # listitem
    listitem = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
    listitem.setInfo(type='video',
                     infoLabels={'title':name,
                                 'plot':description})
    # context menu
    contextMenu = []
    if showcontext == 'smartlist':
        # スマートリストを編集
        action = 'XBMC.RunPlugin(%s?mode=63&name=%s)' % (sys.argv[0], urllib.quote_plus(name.encode('utf-8','ignore')))
        contextMenu.append((addon.getLocalizedString(30904),action))
        # スマートリストを削除
        action = 'XBMC.RunPlugin(%s?mode=64&name=%s)' % (sys.argv[0], urllib.quote_plus(name.encode('utf-8','ignore')))
        contextMenu.append((addon.getLocalizedString(30905),action))
    elif showcontext != 'top':
        # トップに戻る
        contextMenu.append((addon.getLocalizedString(30936),'XBMC.Container.Update(%s,replace)' % (sys.argv[0])))
    # アドオン設定
    contextMenu.append((addon.getLocalizedString(30937),'XBMC.RunPlugin(%s?mode=82)' % sys.argv[0]))
    listitem.addContextMenuItems(contextMenu, replaceItems=True)
    # add directory item
    url = '%s?url=%s&mode=%s' % (sys.argv[0], urllib.quote_plus(url), mode)
    return xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


def addItem(item, onair=False):
    # convert to item object
    item = Item(item)
    # listitem
    thumbnail = item.thumbnail()
    listitem = xbmcgui.ListItem(item.title(onair), iconImage=thumbnail, thumbnailImage=thumbnail)
    listitem.setInfo(type='video',
                     infoLabels={'title':item.title(onair),
                                 'plot':item.plot(),
                                 'plotoutline':item.outline(),
                                 'studio':item.studio(),
                                 'genre':item.genre(),
                                 'date':item.date(),
                                 'duration':item.duration(onair)})
    listitem.setProperty('IsPlayable', 'true')
    # context menu
    listitem.addContextMenuItems(item.contextmenu(sys), replaceItems=True)
    # add directory item
    return xbmcplugin.addDirectoryItem(int(sys.argv[1]), item.link(), listitem, False)


def main():
    # パラメータ抽出
    params = {'mode':'', 'url':'', 'name':''}
    if len(sys.argv[2]) > 0:
        pairs = re.compile(r'[?&]').split(sys.argv[2])
        for i in range(len(pairs)):
            splitparams = pairs[i].split('=')
            if len(splitparams) == 2:
                params[splitparams[0]] = splitparams[1]
    mode = params['mode']
    url = urllib.unquote_plus(str(params['url'])) # str
    name = urllib.unquote_plus(str(params['name'])).decode('utf-8') # unicode

    # 設定
    status = setupSettings()
    if mode == '' and status == False:
        xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])
        return
    # ログ
    addon_debug('mode: %s' % mode)
    addon_debug('url:  %s' % url)
    addon_debug('name: %s' % name)
    for argv in sys.argv: addon_debug('argv: %s' % argv)

    # キャッシュサイズが未設定の場合は設定
    if addon.getSetting('cache') == '': Cache().update()

    # 各種処理
    if mode=='':
        browseGaraponTV('top')

    # browse
    elif mode=='11':
        browseGaraponTV('date', url)

    elif mode=='12':
        browseGaraponTV('channel', url)

    elif mode=='13':
        browseGaraponTV('genre', url)

    elif mode=='14':
        browseGaraponTV('subgenre', url)

    # search
    elif mode=='15':
        result = searchGaraponTV(url)
        if result != 'success':
            notify(result)

    # search onair
    elif mode=='16':
        sdate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        result = searchGaraponTV(url+'&dt=e&sdate='+sdate, onair=True)
        if result != 'success':
            notify(result)
        else:
            updateOnAir()

    # browse downloads
    elif mode=='17':
        browseDownloads()

    # manage favorites
    elif mode=='20':
        result = manageFavorites(url)
        if result != 'success':
            notify(result)
        else:
            # refresh contextmenus
            xbmc.executebuiltin('XBMC.Container.Refresh')

    # manage downloads
    elif mode=='30':
        result = Downloads().add(url)
        if result != 'success':
            notify(result)
        else:
            # refresh contextmenus
            xbmc.executebuiltin('XBMC.Container.Refresh')

    elif mode=='31':
        result = Downloads().delete(url)
        if result != 'success':
            notify(result)
        else:
            # refresh contextmenus
            xbmc.executebuiltin('XBMC.Container.Refresh')

    elif mode=='32':
        Downloads().clear()
        # refresh top page
        xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])

    elif mode=='33':
        Downloads().createRSS()
        # refresh top page
        xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])

    # smartlist
    elif mode=='60':
        SmartList().clear()
        # open settings
        xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='61':
        SmartList().set(name, url)
        # open settings
        xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='62':
        SmartList().add()
        # refresh top page
        xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])

    elif mode=='63':
        SmartList().edit(name)
        # open settings
        xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=83)' % sys.argv[0])

    elif mode=='64':
        SmartList().delete(name)
        # refresh top page
        xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])

    # settings
    elif mode=='70':
        if addon.getSetting('garapon_auto') == 'true':
            result = initializeNetwork()
        else:
            result = 'success'
        if result == 'success':
            xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=71,replace)' % sys.argv[0])
        else:
            notify(result)
            xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])

    elif mode=='71':
        result = initializeSession()
        if result == 'success':
            xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=72,replace)' % sys.argv[0])
        else:
            notify(result)
            xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])

    elif mode=='72':
        result = initializeChannel()
        if result == 'success':
            if setupSettings():
                # refresh top page
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])
            else:
                notify('Setup settings failed')
                xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])
        else:
            notify(result)
            xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])

    # update session only
    elif mode=='73':
        result = initializeSession()
        if result == 'success':
            if setupSettings():
                # refresh top page
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])
            else:
                notify('Setup settings failed')
                xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])
        else:
            notify(result)

    # update channel only
    elif mode=='74':
        result = initializeChannel()
        if result == 'success':
            if setupSettings():
                # refresh top page
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % sys.argv[0])
            else:
                notify('Setup settings failed')
                xbmc.executebuiltin('XBMC.RunPlugin(%s?mode=82)' % sys.argv[0])
        else:
            notify(result)

    # cache
    elif mode=='80':
        Cache().clear()
        Cache().update()

    # radiruko
    elif mode=='81':
        xbmc.executebuiltin('XBMC.RunAddon(%s)' % radiruko)

    # settings
    elif mode=='82':
        # clear smartlist
        SmartList().clear()
        # update cache settings
        Cache().update()
        # open settings
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % garapon)

    elif mode=='83':
        # update cache settings
        Cache().update()
        # open settings & focus smartlist category
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % garapon)
        xbmc.executebuiltin('SetFocus(102)') # smartlist category which is the 3rd
        xbmc.executebuiltin('SetFocus(215)') # keyword control which is the 16th including hidden controls

    elif mode=='84':
        # sync gtvsession
        result = syncSession(url);
        if result != 'success':
            notify(result)

    elif mode=='85':
        # add to smartlist
        SmartList().set(name, url)
        SmartList().add()


def syncSession(url):
    # パラメータ抽出
    params = {'credential':'', 'gtvsession':'', 'authtime':''}
    pairs = re.compile(r'[?&]').split(url)
    for i in range(len(pairs)):
        splitparams = pairs[i].split('=')
        if len(splitparams) == 2:
            params[splitparams[0]] = splitparams[1]
    # 抽出された値
    url = pairs[0]
    credential = params['credential']
    gtvsession = params['gtvsession']
    authtime = params['authtime']
    # 最新のgtvsessionを判定
    if float(settings['authtime']) > float(authtime):
        gtvsession = settings['session']
        authtime = settings['authtime']
        authupdate = True
    else:
        addon.setSetting('garapon_session', gtvsession)
        addon.setSetting('garapon_authtime', authtime)
        authupdate = False
    # サーバへ最新のgtvsessionを通知
    url = '%s?credential=%s&gtvsession=%s&authtime=%s&authupdate=%s' % (url, credential, gtvsession, authtime, str(authupdate))
    req = urllib2.Request(url, '')
    try:
        response = urllib2.urlopen(req)
    except HTTPError, e:
        addon_error('syncSession: HTTPError: %s' % str(e.code))
        return 'syncSession failed'
    except URLError, e:
        addon_error('syncSession: URLError: %s' % str(e.reason))
        return 'syncSessionn failed'
    response_body = response.read()
    response.close()
    return 'success'


def checkOnAir(programs):
    # 放送中の番組の終了時刻を計算
    enddate = []
    for item in programs:
        if item['ts'] == 1:
            try:
                t = datetime.datetime.strptime(item['startdate'], '%Y-%m-%d %H:%M:%S')
            except TypeError:
                t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(item['startdate'],'%Y-%m-%d %H:%M:%S')))
            a = item['duration'].split(':')
            t = t + datetime.timedelta(seconds=int(a[2]),minutes=int(a[1]),hours=int(a[0]))
            t = time.mktime(t.timetuple())
            enddate.append(int(t))
    return min(enddate)


def updateOnAir1(id):
    # idをチェック
    if os.path.isfile(RESUME_FILE) and id == os.path.getmtime(RESUME_FILE):
        # ウィンドウをチェック
        path = xbmc.getInfoLabel('Container.FolderPath')
        if path ==  sys.argv[0] + '?mode=16&url=n%3d100%26p%3d1%26video%3dall':
            updateOnAir()


def updateOnAir():
    # 現在時刻
    now = time.time()
    if now > nextAired:
        xbmc.executebuiltin('XBMC.Container.Refresh')
        addon_debug('updateOnAir: xbmc.executebuiltin')
    else:
        # 遅延を設定
        delay = nextAired - now + 30
        if delay < 0: delay = 0
        # idを設定
        f = codecs.open(RESUME_FILE,'w','utf-8')
        f.write('')
        f.close()
        id = os.path.getmtime(RESUME_FILE)
        # スレッドを起動
        threading.Timer(delay, updateOnAir1, args=[id]).start()
        addon_debug('updateOnAir: threading.Timer.start: %d %f' % (id,delay))


if __name__  == '__main__': main()
