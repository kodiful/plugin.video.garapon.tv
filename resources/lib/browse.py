# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys, os
import datetime, time
import re, math
import urllib, urlparse
import json
import codecs
import threading
import xbmc,xbmcaddon,xbmcgui,xbmcplugin

from common import log,notify,isholiday
from channel import Channel
from genre import Genre
from smartlist import SmartList
from request import Request
from const import Const
from item import Item

from initialize import initializeSession,checkSettings

#-------------------------------------------------------------------------------
class Browse:

    def __init__(self, query=None):
        self.query = query or 'n=%d&p=1&video=all' % (Const.ITEMS)
        self.args = urlparse.parse_qs(self.query, keep_blank_values=True)
        for key in self.args.keys(): self.args[key] = self.args[key][0]

    def show(self, action):
        if action == 'top':
            self.show_top()
        elif action == 'date':
            self.show_date()
        elif action == 'channel':
            self.show_channel()
        elif action == 'genre':
            self.show_genre()
        elif action == 'subgenre':
            self.show_subgenre()
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_top(self):
        #放送中の番組
        self.add_directory_item(Const.STR(30916),self.query,16,context='top',thumbnail=Const.RETRO_TV)
        #検索:日付
        self.add_directory_item(Const.STR(30933),'',11,context='top',thumbnail=Const.CALENDAR)
        #検索:チャンネル
        self.add_directory_item(Const.STR(30934),'',12,context='top',thumbnail=Const.RADIO_TOWER)
        #検索:ジャンル
        self.add_directory_item(Const.STR(30935),'',13,context='top',thumbnail=Const.CATEGORIZE)
        #お気に入り
        self.add_directory_item(Const.STR(30923),self.query+'&rank=all',15,context='top',thumbnail=Const.FAVORITE_FOLDER)
        #ダウンロード
        if Const.PLUS_ADDON:
            listitem = xbmcgui.ListItem(Const.PLUS_ADDON.getLocalizedString(30927), iconImage=Const.DOWNLOADS_FOLDER, thumbnailImage=Const.DOWNLOADS_FOLDER)
            url = 'plugin://%s' % Const.PLUS_ADDON_ID
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)
        #スマートリスト
        for i in SmartList().getList():
            title = i['title']
            query = i['query']
            self.add_directory_item(title,query,15,context='smartlist',thumbnail=Const.BROWSE_FOLDER)

    def show_date(self):
        #すべての日付
        name = '[COLOR green]%s[/COLOR]' % Const.STR(30912)
        if self.args.get('ch',None) is None:
            mode = 12
        elif self.args.get('genre0',None) is None:
            mode = 13
        else:
            mode = 15
        self.add_directory_item(name,self.query+'&sdate=&edate=',mode,thumbnail=Const.CALENDAR)
        #月,火,水,木,金,土,日
        w = Const.STR(30920).split(',')
        for i in range(120):
            d = datetime.date.today() - datetime.timedelta(i)
            wd = d.weekday()
            #月日
            date1 = d.strftime(Const.STR(30919).encode('utf-8','ignore')).decode('utf-8')  + '(' + w[wd]+ ')'
            date2 = d.strftime('%Y-%m-%d')
            if isholiday(date2) or wd == 6:
                name = '[COLOR red]%s[/COLOR]' % date1
            elif wd == 5:
                name = '[COLOR blue]%s[/COLOR]' % date1
            else:
                name = date1
            query = '%s&sdate=%s 00:00:00&edate=%s 23:59:59' % (self.query,date2,date2)
            if self.args.get('ch',None) is None:
                mode = 12
            elif self.args.get('genre0',None) is None:
                mode = 13
            else:
                mode = 15
            self.add_directory_item(name,query,mode,thumbnail=Const.CALENDAR)

    def show_channel(self):
        for ch in Channel().getList():
            name = ch['name']
            id = ch['id']
            if self.args.get('genre0',None) is None:
                mode = 13
            elif self.args.get('sdate',None) is None:
                mode = 11
            else:
                mode = 15
            query = '%s&%s' % (self.query, urllib.urlencode({'ch':id}))
            self.add_directory_item(name,query,mode,thumbnail=Const.RADIO_TOWER)

    def show_genre(self):
        for i in Genre().getList():
            name = i['name']
            id = i['id']
            if id == '':
                if self.args.get('ch',None) is None:
                    mode = 12
                elif self.args.get('sdate',None) is None:
                    mode = 11
                else:
                    mode = 15
                query = '%s&%s' % (self.query, urllib.urlencode({'genre0':'','genre1':''}))
                self.add_directory_item(name,query,mode,thumbnail=Const.CATEGORIZE)
            else:
                query = '%s&%s' % (self.query, urllib.urlencode({'genre0':id}))
                self.add_directory_item(name,query,14,thumbnail=Const.CATEGORIZE)

    def show_subgenre(self):
        genre0 = re.search('&genre0=([0-9]+)',self.query).group(1)
        for i in Genre().getList(genre0):
            name = i['name']
            id = i['id']
            if self.args.get('ch',None) is None:
                mode = 12
            elif self.args.get('sdate',None) is None:
                mode = 11
            else:
                mode = 15
            query = '%s&%s' % (self.query, urllib.urlencode({'genre1':id}))
            self.add_directory_item(name,query,mode,thumbnail=Const.CATEGORIZE)

    def favorites(self):
        # 検索
        response_body = Request().favorites(self.query)
        if response_body:
            response_data = json.loads(response_body)
            if response_data['status'] == 1:
                xbmc.executebuiltin('Container.Refresh')
            else:
                log('switch favorites failed', error=True)
                notify('Operation failed')
        else:
            log('empty response', error=True)
            notify('Operation failed')

    def search(self, onair=False, retry=True):
        # 検索
        response_body = Request().search(self.query)
        if response_body:
            response_data = json.loads(response_body)
            if response_data['status'] == 1:
                # 検索結果の番組
                programs = response_data['program']
                if onair:
                    # 放送中の番組はチャンネル順
                    for item in sorted(programs, key=lambda item: item['ch']):
                        if item['ts'] == 1: self.add_item(item, onair)
                    # 放送中の番組の更新を設定
                    UpdateOnAir(programs).set_timer()
                else:
                    # 放送済みの番組は時間降順
                    for item in sorted(programs, key=lambda item: item['startdate'], reverse=True):
                        if item['ts'] == 1: self.add_item(item, onair)
                # 検索結果の続きがある場合は次のページへのリンクを表示
                hit = int(response_data['hit'])
                page = int(self.args.get('p'))
                if hit > page * Const.ITEMS:
                    self.args['p'] = page+1
                    query = urllib.urlencode(self.args)
                    #次のページへ
                    self.add_directory_item('[COLOR green]%s[/COLOR]' % (Const.STR(30922)),query,15,thumbnail=Const.RIGHT)
                # end of directory
                xbmcplugin.endOfDirectory(int(sys.argv[1]))
            elif retry == True:
                # セッションを初期化してリトライする
                if initializeSession():
                    if checkSettings():
                        self.search(onair, retry=False)
                    else:
                        log('invalid settings', error=True)
                        notify('Search failed')
                else:
                    log('session initialization failed', error=True)
                    notify('Search failed')
            else:
                # リトライも失敗
                log('retry failed', error=True)
                notify('Search failed')
        else:
            log('empty response', error=True)
            notify('Search failed')

    def add_item(self, item, onair=False):
        # listitem
        item = Item(item, onair)
        listitem = xbmcgui.ListItem(item.title, iconImage=item.thumbnail, thumbnailImage=item.thumbnail)
        listitem.setInfo(type='video',
                         infoLabels={'title':item.title,
                                     'plot':item.plot,
                                     'plotoutline':item.outline,
                                     'studio':item.studio,
                                     'genre':item.genre,
                                     'date':item.date,
                                     'duration':item.duration})
        listitem.setProperty('IsPlayable', 'true')
        # context menu
        listitem.addContextMenuItems(item.contextmenu, replaceItems=True)
        # add directory item
        return xbmcplugin.addDirectoryItem(int(sys.argv[1]), item.link, listitem, False)

    def add_directory_item(self, name, url, mode, context='', thumbnail=''):
        # listitem
        listitem = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
        # context menu
        contextMenu = []
        if context == 'smartlist':
            # スマートリストを編集
            action = 'RunPlugin(%s?mode=63&name=%s)' % (sys.argv[0], urllib.quote_plus(name.encode('utf-8','ignore')))
            contextMenu.append((Const.STR(30904),action))
            # スマートリストを削除
            action = 'RunPlugin(%s?mode=64&name=%s)' % (sys.argv[0], urllib.quote_plus(name.encode('utf-8','ignore')))
            contextMenu.append((Const.STR(30905),action))
        elif context != 'top':
            # トップに戻る
            action = 'Container.Update(%s,replace)' % (sys.argv[0])
            contextMenu.append((Const.STR(30936),action))
        # アドオン設定
        contextMenu.append((Const.STR(30937),'RunPlugin(%s?mode=82)' % sys.argv[0]))
        listitem.addContextMenuItems(contextMenu, replaceItems=True)
        # add directory item
        url = '%s?url=%s&mode=%s' % (sys.argv[0], urllib.quote_plus(url), mode)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)

#-------------------------------------------------------------------------------
class UpdateOnAir:

    def __init__(self, programs):
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
        self.next_aired = min(enddate)

    def set_timer(self):
        # 現在時刻
        now = time.time()
        if now > self.next_aired:
            xbmc.executebuiltin('Container.Refresh')
            log('updateOnAir: xbmc.executebuiltin')
        else:
            # 遅延を設定
            delay = self.next_aired - now + 30
            if delay < 0: delay = 0
            # idを設定
            f = codecs.open(Const.RESUME_FILE,'w','utf-8')
            f.write('')
            f.close()
            id = os.path.getmtime(Const.RESUME_FILE)
            # スレッドを起動
            threading.Timer(delay, self.check_onair, args=[id]).start()
            log('updateOnAir: threading.Timer.start: %d %f' % (id,delay))

    def check_onair(self, id):
        # idをチェック
        if os.path.isfile(Const.RESUME_FILE) and id == os.path.getmtime(Const.RESUME_FILE):
            # ウィンドウをチェック
            path = xbmc.getInfoLabel('Container.FolderPath')
            if path ==  sys.argv[0] + '?mode=16&url=n%3d100%26p%3d1%26video%3dall':
                self.set_timer()
