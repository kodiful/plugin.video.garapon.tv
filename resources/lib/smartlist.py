# -*- coding: utf-8 -*-

from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.channel import Channel
from resources.lib.genre import Genre


class SmartList():

    def __init__(self, settings={}):
        self.settings = settings

    def getList(self):
        return Common.read_json(Common.SMARTLIST_FILE) or []

    def setList(self, data):
        Common.write_json(Common.SMARTLIST_FILE, sorted(data, key=lambda item: item['query']))

    def beginEdit(self, name, ch, g0, g1):
        if ch:
            # keyword
            Common.SET('keyword', name)
            # channel
            channel = Channel().search(ch)
            Common.SET('channel', channel['name'])
            # genre
            genre = Genre().search(g0, g1)
            Common.SET('g0', genre['name0'])
            Common.SET(genre['id'], genre['name1'])
        else:
            # スマートリストでtitleが一致するものをダイアログに設定
            for item in filter(lambda x: x['title'] == name, self.getList()):
                for key, val in item.items():
                    Common.log(key, val)
                    Common.SET(key, val)

    def endEdit(self):
        # 既存のスマートリストからqueryが一致するものを削除
        query = self.settings.get('query')
        smartlist = list(filter(lambda x: x['query'] != query, self.getList()))
        # ダイアログの設定を取得
        source = self.settings.get('source')
        keyword = self.settings.get('keyword')
        # channel
        str2 = self.settings.get('channel')
        channel = Channel().search(str2)
        # genre
        str0 = self.settings.get('g0')
        genre = Genre().search(str0)
        str1 = self.settings.get(genre['id'])
        genre = Genre().search(str0, str1)
        # query
        args = {
            'n': Common.ITEMS,
            'p': 1,
            'video': 'all',
            'key': keyword,
            's': ['e', 'c'][int(source)],
            'ch': channel['id'],
            'g0': genre['id0'],
            'g1': genre['id1']
        }
        # データを追加
        data = {
            'title': keyword,
            'query': urlencode(args),
            'channel': str2,
            'source': source,
            'keyword': keyword
        }
        if genre['id0']:
            data['g0'] = str0
        if genre['id1']:
            data[genre['id']] = str1
        smartlist.append(data)
        # ファイルに書き込む
        self.setList(smartlist)

    def delete(self, name):
        self.setList(filter(lambda x: x['title'] != name, self.getList()))
