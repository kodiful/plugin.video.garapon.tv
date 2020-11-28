# -*- coding: utf-8 -*-

import sys, os
import datetime, time
import re, math
import urllib, urlparse
import json
import threading
import xbmc,xbmcaddon,xbmcgui,xbmcplugin

from common import *
from channel import Channel
from genre import Genre
from smartlist import SmartList
from request import Request
from const import Const
from item import Item
from downloader import Downloader

from initialize import initializeSession, checkSettings


class Browse:

    def __init__(self, query=None):
        self.query = query or 'n=%d&p=1&video=all' % (Const.ITEMS)
        self.args = urlparse.parse_qs(self.query, keep_blank_values=True)
        for key in self.args.keys(): self.args[key] = self.args[key][0]

    def top(self):
        #放送中の番組
        self.add_directory_item(Const.STR(30916),self.query,16,context='top',iconimage=Const.RETRO_TV)
        #検索:日付
        self.add_directory_item(Const.STR(30933),'',11,context='top',iconimage=Const.CALENDAR)
        #検索:チャンネル
        self.add_directory_item(Const.STR(30934),'',12,context='top',iconimage=Const.RADIO_TOWER)
        #検索:ジャンル
        self.add_directory_item(Const.STR(30935),'',13,context='top',iconimage=Const.CATEGORIZE)
        #お気に入り
        self.add_directory_item(Const.STR(30923),self.query+'&rank=all',15,context='top',iconimage=Const.FAVORITE_FOLDER)
        #ダウンロード
        Downloader().top(Const.DOWNLOADS_FOLDER)
        #スマートリスト
        for i in SmartList().getList():
            title = i['title']
            query = i['query']
            self.add_directory_item(title,query,15,context='smartlist',iconimage=Const.BROWSE_FOLDER)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_date(self):
        #すべての日付
        name = '[COLOR green]%s[/COLOR]' % Const.STR(30912)
        if self.args.get('ch',None) is None:
            mode = 12
        elif self.args.get('genre0',None) is None:
            mode = 13
        else:
            mode = 15
        self.add_directory_item(name,self.query+'&sdate=&edate=',mode,iconimage=Const.CALENDAR)
        #月,火,水,木,金,土,日
        w = Const.STR(30920).encode('utf-8').split(',')
        for i in range(120):
            d = datetime.date.today() - datetime.timedelta(i)
            wd = d.weekday()
            #月日
            log(type(w[wd]))
            date1 = d.strftime(Const.STR(30919).encode('utf-8')) + '(' + w[wd]+ ')'
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
            self.add_directory_item(name,query,mode,iconimage=Const.CALENDAR)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_channel(self):
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
            self.add_directory_item(name,query,mode,iconimage=Const.RADIO_TOWER)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_genre(self):
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
                self.add_directory_item(name,query,mode,iconimage=Const.CATEGORIZE)
            else:
                query = '%s&%s' % (self.query, urllib.urlencode({'genre0':id}))
                self.add_directory_item(name,query,14,iconimage=Const.CATEGORIZE)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_subgenre(self):
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
            self.add_directory_item(name,query,mode,iconimage=Const.CATEGORIZE)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
                        if item.get('ts') == 1: self.add_item(item, onair)
                    # 放送中の番組の更新を設定
                    UpdateOnAir(programs).set_timer()
                else:
                    # 放送済みの番組は時間降順
                    for item in sorted(programs, key=lambda item: item['startdate'], reverse=True):
                        if item.get('ts') == 1: self.add_item(item, onair)
                # 検索結果の続きがある場合は次のページへのリンクを表示
                hit = int(response_data['hit'])
                page = int(self.args.get('p'))
                if hit > page * Const.ITEMS:
                    self.args['p'] = page+1
                    query = urllib.urlencode(self.args)
                    #次のページへ
                    self.add_directory_item('[COLOR green]%s[/COLOR]' % (Const.STR(30922)),query,15,iconimage=Const.RIGHT)
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
        s = item.item['_summary']
        labels = {
            'title': s['title'],
            'plot': '%s\n%s' % (s['date'], s['description']),
            'plotoutline': s['description'],
            'studio': s['source'],
            'genre': s['category'],
            'date': s['date'],
            'duration': s['duration'],
        }
        listitem = xbmcgui.ListItem(item.title())
        listitem.setArt({'icon':s['thumbnail'], 'thumb':s['thumbnail'], 'poster':s['thumbnail']})
        listitem.setInfo(type='video', infoLabels=labels)
        listitem.setProperty('IsPlayable', 'true')
        # context menu
        listitem.addContextMenuItems(item.contextmenu, replaceItems=True)
        # add directory item
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), s['url'], listitem, False)

    def add_directory_item(self, name, url, mode, context='', iconimage=''):
        # listitem
        listitem = xbmcgui.ListItem(name)
        listitem.setArt({'icon':iconimage})
        # context menu
        contextMenu = []
        if context == 'smartlist':
            # スマートリストを編集
            action = 'RunPlugin(%s?mode=63&name=%s)' % (sys.argv[0], urllib.quote_plus(name))
            contextMenu.append((Const.STR(30904),action))
            # スマートリストを削除
            action = 'RunPlugin(%s?mode=64&name=%s)' % (sys.argv[0], urllib.quote_plus(name))
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
            with open(Const.RESUME_FILE, 'w') as f:
                f.write('')
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
