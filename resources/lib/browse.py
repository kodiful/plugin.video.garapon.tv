# -*- coding: utf-8 -*-

import sys
import os
import datetime
import time
import json
import threading

from urllib.parse import parse_qs
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.common import Common
from resources.lib.channel import Channel
from resources.lib.genre import Genre
from resources.lib.smartlist import SmartList
from resources.lib.request import Request
from resources.lib.item import Item
from resources.lib.downloader import Downloader
from resources.lib.holiday import Holiday

from resources.lib.initialize import initializeSession
from resources.lib.initialize import checkSettings


class Browse(Common):

    def __init__(self, query=None):
        self.query = query or 'n=%d&p=1&video=all' % (self.ITEMS)
        self.args = parse_qs(self.query, keep_blank_values=True)
        for key in self.args.keys():
            self.args[key] = self.args[key][0]
        # 祝祭日判定
        self.holiday = Holiday(os.path.join(self.DATA_PATH, 'data.db'))

    def top(self):
        # 放送中の番組
        self.add_directory_item(self.STR(30916), self.query, 'searchOnAir', context='top', iconimage=self.RETRO_TV)
        # 検索:日付
        self.add_directory_item(self.STR(30933), '', 'selectDate', context='top', iconimage=self.CALENDAR)
        # 検索:チャンネル
        self.add_directory_item(self.STR(30934), '', 'selectChannel', context='top', iconimage=self.RADIO_TOWER)
        # 検索:ジャンル
        self.add_directory_item(self.STR(30935), '', 'selectGenre', context='top', iconimage=self.CATEGORIZE)
        # お気に入り
        self.add_directory_item(self.STR(30923), '%s&rank=all' % self.query, 'search', context='top', iconimage=self.FAVORITE_FOLDER)
        # ダウンロード
        Downloader().top(self.DOWNLOADS_FOLDER)
        # スマートリスト
        for i in SmartList().getList():
            title = i['title']
            query = i['query']
            self.add_directory_item(title, query, 'search', context='smartlist', iconimage=self.BROWSE_FOLDER)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_date(self):
        # すべての日付
        name = '[COLOR lightgreen]%s[/COLOR]' % self.STR(30912)
        if self.args.get('ch') is None:
            mode = 'selectChannel'
        elif self.args.get('genre0') is None:
            mode = 'selectGenre'
        else:
            mode = 'search'
        self.add_directory_item(name, '%s&sdate=&edate=' % self.query, mode, iconimage=self.CALENDAR)
        # 月,火,水,木,金,土,日
        for i in range(120):
            d = datetime.date.today() - datetime.timedelta(i)
            date = d.strftime('%Y-%m-%d')
            name = self.holiday.convert(date, self.STR(30919))
            query = '%s&sdate=%s 00:00:00&edate=%s 23:59:59' % (self.query, date, date)
            if self.args.get('ch') is None:
                mode = 'selectChannel'
            elif self.args.get('genre0') is None:
                mode = 'selectGenre'
            else:
                mode = 'search'
            self.add_directory_item(name, query, mode, iconimage=self.CALENDAR)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_channel(self):
        for ch in Channel().getList():
            name = ch['name']
            id = ch['id']
            if self.args.get('genre0') is None:
                mode = 'selectGenre'
            elif self.args.get('sdate') is None:
                mode = 'selectDate'
            else:
                mode = 'search'
            query = '%s&%s' % (self.query, urlencode({'ch': id}))
            self.add_directory_item(name, query, mode, iconimage=self.RADIO_TOWER)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_genre(self):
        for i in Genre().getList():
            name = i['name']
            id = i['id']
            if id == '':
                if self.args.get('ch') is None:
                    mode = 'selectChannel'
                elif self.args.get('sdate') is None:
                    mode = 'selectDate'
                else:
                    mode = 'search'
                query = '%s&%s' % (self.query, urlencode({'genre0': '', 'genre1': ''}))
                self.add_directory_item(name, query, mode, iconimage=self.CATEGORIZE)
            else:
                query = '%s&%s' % (self.query, urlencode({'genre0': id}))
                self.add_directory_item(name, query, 'selectSubgenre', iconimage=self.CATEGORIZE)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_subgenre(self):
        genre0 = self.args['genre0']
        for genre1 in Genre().getList(genre0):
            id = genre1['id']
            name = genre1['name']
            if self.args.get('ch') is None:
                mode = 'selectChannel'
            elif self.args.get('sdate') is None:
                mode = 'selectDate'
            else:
                mode = 'search'
            query = '%s&%s' % (self.query, urlencode({'genre1': id}))
            self.add_directory_item(name, query, mode, iconimage=self.CATEGORIZE)
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
                self.log('switch favorites failed (status=%s)' % response_data['status'], error=True)
                self.notify('Operation failed')
        else:
            self.log('empty response', error=True)
            self.notify('Operation failed')

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
                        if item.get('ts') == 1:
                            self.add_item(item, onair)
                    # 放送中の番組の更新を設定
                    UpdateOnAir(programs).set_timer()
                else:
                    # 放送済みの番組は時間降順
                    for item in sorted(programs, key=lambda item: item['startdate'], reverse=True):
                        if item.get('ts') == 1:
                            self.add_item(item, onair)
                # 検索結果の続きがある場合は次のページへのリンクを表示
                hit = int(response_data['hit'])
                page = int(self.args.get('p'))
                if hit > page * self.ITEMS:
                    self.args['p'] = page + 1
                    query = urlencode(self.args)
                    # 次のページへ
                    self.add_directory_item('[COLOR lightgreen]%s[/COLOR]' % (self.STR(30922)), query, 'search', iconimage=self.RIGHT)
                # end of directory
                xbmcplugin.endOfDirectory(int(sys.argv[1]))
            elif retry is True:
                # セッションを初期化してリトライする
                if initializeSession():
                    if checkSettings():
                        self.search(onair, retry=False)
                    else:
                        self.log('invalid settings', error=True)
                        self.notify('Search failed')
                else:
                    self.log('session initialization failed', error=True)
                    self.notify('Search failed')
            else:
                # リトライも失敗
                self.log('retry failed', error=True)
                self.notify('Search failed')
        else:
            self.log('empty response', error=True)
            self.notify('Search failed')

    def play(self, stream):
        listitem = xbmcgui.ListItem(path=stream)
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

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
            'dateadded': s['date'],
            'duration': s['duration'],
        }
        listitem = xbmcgui.ListItem(item.title())
        listitem.setArt({'icon': s['thumbnail'], 'thumb': s['thumbnail'], 'poster': s['thumbnail']})
        listitem.setInfo(type='video', infoLabels=labels)
        listitem.setProperty('IsPlayable', 'true')
        # context menu
        listitem.addContextMenuItems(item.contextmenu, replaceItems=True)
        # add directory item
        url = '%s?%s' % (sys.argv[0], urlencode({'mode': 'play', 'stream': s['url']}))
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, False)

    def add_directory_item(self, name, url, mode, context='', iconimage=''):
        # listitem
        listitem = xbmcgui.ListItem(name)
        listitem.setArt({'icon': iconimage})
        # context menu
        contextMenu = []
        if context == 'smartlist':
            # スマートリストを編集
            contextMenu.append((
                self.STR(30904),
                'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'mode': 'beginEditSmartList', 'name': name}))))
            # スマートリストを削除
            contextMenu.append((
                self.STR(30905),
                'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'mode': 'deleteSmartList', 'name': name}))))
        elif context != 'top':
            # トップに戻る
            contextMenu.append((
                self.STR(30936),
                'Container.Update(%s,replace)' % (sys.argv[0])))
        # アドオン設定
        contextMenu.append((self.STR(30937), 'RunPlugin(%s?mode=openSettings)' % sys.argv[0]))
        listitem.addContextMenuItems(contextMenu, replaceItems=True)
        # add directory item
        url = '%s?%s' % (sys.argv[0], urlencode({'mode': mode, 'url': url}))
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)


class UpdateOnAir(Common):

    def __init__(self, programs):
        enddate = []
        for item in programs:
            if item['ts'] == 1:
                try:
                    t = datetime.datetime.strptime(item['startdate'], '%Y-%m-%d %H:%M:%S')
                except TypeError:
                    t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(item['startdate'], '%Y-%m-%d %H:%M:%S')))
                a = item['duration'].split(':')
                t = t + datetime.timedelta(seconds=int(a[2]), minutes=int(a[1]), hours=int(a[0]))
                t = time.mktime(t.timetuple())
                enddate.append(int(t))
        self.next_aired = min(enddate)

    def set_timer(self):
        # 現在時刻
        now = time.time()
        if now > self.next_aired:
            xbmc.executebuiltin('Container.Refresh')
            self.log('updateOnAir: xbmc.executebuiltin')
        else:
            # 遅延を設定
            delay = self.next_aired - now + 30
            if delay < 0:
                delay = 0
            # idを設定
            self.write_file(self.RESUME_FILE, '')
            id = os.path.getmtime(self.RESUME_FILE)
            # スレッドを起動
            threading.Timer(delay, self.check_onair, args=[id]).start()
            self.log('updateOnAir: threading.Timer.start: %d %f' % (id, delay))

    def check_onair(self, id):
        # idをチェック
        if os.path.isfile(self.RESUME_FILE) and id == os.path.getmtime(self.RESUME_FILE):
            # ウィンドウをチェック
            path = xbmc.getInfoLabel('Container.FolderPath')
            if path == sys.argv[0] + '?mode=searchOnAir&url=n%3d100%26p%3d1%26video%3dall':
                self.set_timer()
