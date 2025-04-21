# -*- coding: utf-8 -*-

import sys
import shutil
import threading
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs

import xbmc

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.channel import Channel
from resources.lib.genre import Genre
from resources.lib.item import Item


class Smartlist(Common):

    def __init__(self):
        # DBインスタンス
        self.db = ThreadLocal.db
        # 引数
        args = parse_qs(sys.argv[2][1:], keep_blank_values=True)
        self.args = dict(map(lambda x: (x[0], x[1][0]), args.items()))

    def edit(self):
        if self.args.get('status') is None:
            self._preprocess()
        else:
            self._postprocess()

    def _preprocess(self):
        # 一旦デフォルト設定に戻す
        self.clear()
        # 取得した値に設定する
        gtvid = self.args.get('gtvid')
        id = self.args.get('id')
        if gtvid:
            self.db.cursor.execute('SELECT * FROM contents WHERE gtvid = :gtvid', {'gtvid': gtvid})
            data = self.db.cursor.fetchone()
            data = Item(data).smartlist
            self.SET('id', '')
        elif id:
            self.db.cursor.execute('SELECT * FROM smartlist WHERE id = :id', {'id': id})
            data = self.db.cursor.fetchone()
            data = dict(data)
            self.SET('id', id)
        # 設定値を画面に反映する
        self.SET('channel', data['ch_name'])
        self.SET('g', data['genre_name'])
        self.SET('g' + data['genre_id'], data['subgenre_name'])
        self.SET('keyword', data['keyword'])
        self.SET('source', {'e': '0', 'c': '1'}[data.get('source', 'e')])
        # 設定画面の状態を監視する別スレッドを起動する
        thread = threading.Thread(target=self._monitor, daemon=True)
        thread.start()
        # 設定画面を開く
        shutil.copy(Common.SMARTLIST_SETTINGS, Common.SETTINGS_FILE)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)

    def _postprocess(self):
        # 設定値を取得する
        ch = Channel().search(self.GET('channel'))
        ch_id = ch['ch_id']
        ch_name = ch['ch_name']
        g0 = Genre().search(self.GET('g'))
        g1 = Genre().search(self.GET('g'), self.GET('g' + g0['genre_id']))
        genre_id = g1['genre_id']
        genre_name = g1['genre_name']
        subgenre_id = g1['subgenre_id']
        subgenre_name = g1['subgenre_name']
        # DBに反映
        data = {
            'id': self.GET('id') or None,
            'ch_id': ch_id,
            'ch_name': ch_id and ch_name,
            'keyword': self.GET('keyword'),
            'source': {'0': 'e', '1': 'c'}[self.GET('source')],
            'genre_id': genre_id,
            'genre_name': genre_id and genre_name,
            'subgenre_id': subgenre_id,
            'subgenre_name': subgenre_id and subgenre_name
        }
        columns = ','.join(data.keys())
        placeholders = ','.join(['?' for _ in data.values()])
        sql = f'INSERT OR REPLACE INTO smartlist ({columns}) VALUES ({placeholders})'
        self.db.cursor.execute(sql, list(data.values()))
        # トップ画面を表示する
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])

    def _monitor(self):
        # 設定画面が開くのを待つ
        while not xbmc.getCondVisibility("Window.IsActive(10140)"):
            xbmc.sleep(100)
        # 設定画面が閉じるのを待つ
        while xbmc.getCondVisibility("Window.IsActive(10140)"):
            xbmc.sleep(100)
        # 設定処理の開始を待つ
        xbmc.sleep(1000)
        # デフォルト設定に戻す
        self.clear()
        shutil.copy(Common.ORIGINAL_SETTINGS, Common.SETTINGS_FILE)

    def clear(self):
        tree = ET.parse(self.SETTINGS_FILE)
        root = tree.getroot()
        for category in root.findall('category'):
            if category.get('label') == '30000':
                for setting in category.findall('setting'):
                    setting_id = setting.get('id')
                    default = setting.get('default')
                    if setting_id and default is not None:
                        self.SET(setting_id, default)

    def delete(self):
        id = self.args['id']
        self.db.cursor.execute('DELETE FROM smartlist WHERE id = :id', {'id': id})
        xbmc.executebuiltin('Container.Update(%s,replace)' % sys.argv[0])  # refresh top page
