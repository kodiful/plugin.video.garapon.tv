# -*- coding: utf-8 -*-

import sys
import json
from datetime import datetime
from datetime import timedelta
from urllib.parse import parse_qs
from urllib.parse import urlencode

import xbmc
import xbmcgui
import xbmcplugin

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.request import Request
from resources.lib.item import Item
from resources.lib.downloader import Downloader


class Browse(Common):

    # contextmenu flags
    CM_OPEN_SETTINGS = 1 << 0
    CM_RETURN_TO_TOP = 1 << 1
    CM_MANAGE_SMARTLIST = 1 << 2

    def __init__(self):
        # DBインスタンス
        self.db = ThreadLocal.db
        # 引数
        args = parse_qs(sys.argv[2][1:], keep_blank_values=True)
        self.args = dict(map(lambda x: (x[0], x[1][0]), args.items()))

    def top(self):
        # 放送中の番組
        self.add_directory_item(self.STR(30916), 'searchOnAir', {}, iconimage=self.RETRO_TV)
        # 検索:日付
        self.add_directory_item(self.STR(30933), 'selectDate', {}, iconimage=self.CALENDAR)
        # 検索:チャンネル
        self.add_directory_item(self.STR(30934), 'selectChannel', {}, iconimage=self.RADIO_TOWER)
        # 検索:ジャンル
        self.add_directory_item(self.STR(30935), 'selectGenre', {}, iconimage=self.CATEGORIZE)
        # お気に入り
        self.add_directory_item(self.STR(30923), 'searchFavorites', {}, iconimage=self.FAVORITE_FOLDER)
        # ダウンロード
        Downloader().top(self.DOWNLOADS_FOLDER)
        # スマートリスト
        self.db.cursor.execute('SELECT id, keyword FROM smartlist')
        for id, keyword in self.db.cursor.fetchall():
            contextmenu = [
                (self.STR(30904), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'editSmartlist', 'id': id}))),  # スマートリストを編集
                (self.STR(30905), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'deleteSmartlist', 'id': id})))  # スマートリストを削除
            ]
            # listitemを追加
            self.add_directory_item(keyword, 'searchSmartlist', {'id': id}, iconimage=self.BROWSE_FOLDER, contextmenu=contextmenu)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_date(self):
        # 次のアクション
        if self.args.get('ch', '') == '':
            action = 'selectChannel'
        elif self.args.get('genre0', '') == '':
            action = 'selectGenre'
        else:
            action = 'search'
        # 引数
        args = {
            'date': self.args.get('date', ''),
            'ch': self.args.get('ch', ''),
            'genre0': self.args.get('genre0', ''),
            'genre1': self.args.get('genre1', ''),
        }
        # すべての日付
        label = '[COLOR lightgreen]%s[/COLOR]' % self.STR(30912)
        args['date'] = 'all'
        self.add_directory_item(label, action, args, iconimage=self.CALENDAR)
        # 直近の120日間の日付
        for i in range(120):
            d = datetime.now() - timedelta(days=i)
            date = d.strftime('%Y-%m-%d')
            label = self.db.convert(date, self.STR(30919))
            args['date'] = date
            self.add_directory_item(label, action, args, iconimage=self.CALENDAR)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_channel(self):
        # 次のアクション
        if self.args.get('genre0', '') == '':
            action = 'selectGenre'
        elif self.args.get('date', '') == '':
            action = 'selectDate'
        else:
            action = 'search'
        # 引数
        args = {
            'date': self.args.get('date', ''),
            'ch': self.args.get('ch', ''),
            'genre0': self.args.get('genre0', ''),
            'genre1': self.args.get('genre1', ''),
        }
        # チャンネル選択
        self.db.cursor.execute('SELECT ch_id, ch_name FROM channels ORDER BY ch_id')
        for ch_id, ch_name in self.db.cursor.fetchall():
            label = ch_name
            args['ch'] = ch_id or 'all'
            self.add_directory_item(label, action, args, iconimage=self.RADIO_TOWER)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_genre(self):
        # 次のアクション
        action = 'selectSubgenre'
        # 引数
        args = {
            'date': self.args.get('date', ''),
            'ch': self.args.get('ch', ''),
            'genre0': self.args.get('genre0', ''),
            'genre1': self.args.get('genre1', ''),
        }
        # ジャンル選択
        self.db.cursor.execute('SELECT DISTINCT genre_id, genre_name FROM genres ORDER BY genre_id')
        for genre_id, genre_name in self.db.cursor.fetchall():
            label = genre_name
            args['genre0'] = genre_id or 'all'
            self.add_directory_item(label, action, args, iconimage=self.CATEGORIZE)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def select_subgenre(self):
        # 次のアクション
        if self.args.get('ch', '') == '':
            action = 'selectChannel'
        elif self.args.get('date', '') == '':
            action = 'selectDate'
        else:
            action = 'search'
        # 引数
        args = {
            'date': self.args.get('date', ''),
            'ch': self.args.get('ch', ''),
            'genre0': self.args.get('genre0', ''),
            'genre1': self.args.get('genre1', ''),
        }
        # サブジャンル選択
        self.db.cursor.execute('SELECT DISTINCT subgenre_id, subgenre_name FROM genres WHERE genre_id = :genre_id ORDER BY subgenre_id', {'genre_id': self.args.get('genre0')})
        for subgenre_id, subgenre_name in self.db.cursor.fetchall():
            label = subgenre_name
            args['genre1'] = subgenre_id or 'all'
            self.add_directory_item(label, action, args, iconimage=self.CATEGORIZE)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def search(self, target=None):
        # 共通の引数
        args = {
            'n': self.ITEMS,
            'p': self.args.get('page', 1),
            'video': 'all'
        }
        # terget別の引数を追加
        if target is None:
            args.update({
                'sdate': '' if self.args['date'] == 'all' else '%s 00:00:00' % self.args['date'],
                'edate': '' if self.args['date'] == 'all' else '%s 23:59:59' % self.args['date'],
                'ch': '' if self.args['ch'] == 'all' else self.args['ch'],
                'genre0': '' if self.args['genre0'] == 'all' else self.args['genre0'],
                'genre1': '' if self.args['genre1'] == 'all' else self.args['genre1']
            })
        elif target == 'onair':
            args.update({
                'sdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dt': 'e'
            })
        elif target == 'favorites':
            args.update({
                'rank': 'all'
            })
        elif target == 'smartlist':
            sql = 'SELECT * FROM smartlist WHERE id = :id'
            self.db.cursor.execute(sql, {'id': int(self.args['id'])})
            params = self.db.cursor.fetchone()
            args.update({
                'ch': params['ch_id'],
                'key': params['keyword'],
                's': params['source'],
                'genre0': params['genre_id'],
                'genre1': params['subgenre_id']
            })
        # 検索実行
        self._search(target, args)

    def _search(self, target, args):
        response_body = Request().search(urlencode(args))
        response_data = json.loads(response_body)
        '''
        {
            "status": 1,
            "hit": "1",
            "program": [
                {
                    "gtvid": "1SJP7FE21744533000",
                    "startdate": "2025-04-13 17:30:00",
                    "duration": "00:30:00",
                    "ch": "32738",
                    "title": "笑点[解][字]阿佐ヶ谷姉妹がテーマパークをネタに爆笑漫才！好楽がパンツの秘密を暴露！？",
                    "description": "阿佐ヶ谷姉妹の漫才！おばさんの特徴を活かしたネタに会場大爆笑！大喜利は、冷静さを失った昇太がとった驚きの行動に、一之輔が見事な逆襲！小遊三は自分の○○を忘れる!?",
                    "favorite": "0",
                    "audio_ch": "0",
                    "seq_genregtvid_tbl": "4165290",
                    "genre1": "9",
                    "genre2": "3",
                    "genre": [
                        "9/3",
                        "5/3"
                    ],
                    "bc": "日テレ",
                    "bc_tags": "#ntv",
                    "ts": 1
                }
            ],
            "version": "GTV4.2409170",
            "streamsess": "49259df6f9e1a2aaf44c9118ea641d25"
        }
        '''
        # statusコードをチェック
        if response_data['status'] != 1:
            # 1 正常
            # 0 ログインセッションIDもしくはデベロッパーIDが不正
            # 100 パラメータエラー
            # 200 DB接続エラー
            self.notify('Search failed (%d)' % response_data['status'], error=True)
            return
        # DBを更新
        self.db.cursor.execute('DELETE FROM contents')
        for item in response_data['program']:
            if item.get('ts') == 1:
                self.db.add(item)
        # listitemを設定
        if target == 'onair':
            self.db.cursor.execute('SELECT * FROM contents ORDER BY ch ASC')  # 放送中の番組はチャンネル順
            for item in self.db.cursor.fetchall():
                self.add_item(dict(item), onair=True)
        else:
            self.db.cursor.execute('SELECT * FROM contents ORDER BY startdate DESC')  # 放送済みの番組は時間降順
            for item in self.db.cursor.fetchall():
                self.add_item(dict(item), onair=False)
        # 検索結果の続きがある場合は次のページへのリンクを表示
        hit = int(response_data['hit'])
        page = int(int(args['p']))
        if hit > page * self.ITEMS:
            label = '[COLOR lightgreen]%s[/COLOR]' % (self.STR(30922))  # 次のページへ
            self.args.update({'page': page+1})
            self.add_directory_item(label, self.args['action'], self.args, iconimage=self.RIGHT)
        # end of directory
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def play(self, stream):
        listitem = xbmcgui.ListItem()
        listitem.setPath(stream)
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

    def set_favorites(self):
        # 検索
        args = {
            'gtvid': self.args['gtvid'],
            'rank': self.args['rank']
        }
        response_body = Request().favorites(urlencode(args))
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            xbmc.executebuiltin('Container.Refresh')
        else:
            self.notify('Operation failed (%d)' % response_data['status'], error=True)

    def add_item(self, item, onair=False):
        # listitem
        item = Item(item, onair)
        listitem = xbmcgui.ListItem()
        listitem.setLabel(item.label)
        listitem.setInfo(type='video', infoLabels=item.infolabels)
        listitem.setArt(item.art)
        listitem.setProperty('IsPlayable', 'true')
        # context menu
        listitem.addContextMenuItems(item.contextmenu, replaceItems=True)
        # add directory item
        url = '%s?%s' % (sys.argv[0], urlencode({'action': 'play', 'stream': item.content_url}))
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, False)

    def add_directory_item(self, label, action, args, iconimage='', contextmenu=[]):
        # listitem
        listitem = xbmcgui.ListItem(label)
        listitem.setArt({'icon': iconimage})
        # context menu
        contextmenu2 = [(self.STR(30937), 'RunPlugin(%s?action=openSettings)' % sys.argv[0])]  # アドオン設定
        listitem.addContextMenuItems(contextmenu + contextmenu2, replaceItems=True)
        # add directory item
        args.update({'action': action})
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), '%s?%s' % (sys.argv[0], urlencode(args)), listitem, True)

    def contextmenu(self, flags=0, **kwargs):
        contextmenu = []
        # トップに戻る
        if flags & self.CM_RETURN_TO_TOP:
            contextmenu.append((self.STR(30936), 'Container.Update(%s,replace)' % (sys.argv[0])))
        # アドオン設定
        if flags & self.CM_OPEN_SETTINGS:
            contextmenu.append((self.STR(30937), 'RunPlugin(%s?action=openSettings)' % sys.argv[0]))
        # スマートリスト管理
        if flags & self.CM_MANAGE_SMARTLIST:
            # スマートリストを編集
            contextmenu.append((self.STR(30904), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'editSmartlist', 'id': kwargs['id']}))))
            # スマートリストを削除
            contextmenu.append((self.STR(30905), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode({'action': 'deleteSmartlist', 'id': kwargs['id']}))))
        return contextmenu
        
