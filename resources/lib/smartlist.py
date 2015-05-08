# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import codecs
import urllib
import json

from common import(addon,settings)
from common import(SMARTLIST_FILE)

from channel import(Channel)
from genre import(Genre)


class SmartList():
    
    def __init__(self):
        return

    def getList(self):
        if os.path.exists(SMARTLIST_FILE):
            f = codecs.open(SMARTLIST_FILE,'r','utf-8')
            list = json.loads(f.read())
            f.close()
        else:
            list = []
        return list

    def setList(self, list):
        # queryでソート
        list = sorted(list, key=lambda item: item['query'])
        # ファイルに書き込む
        f = codecs.open(SMARTLIST_FILE,'w','utf-8')
        f.write(json.dumps(list))
        f.close()

    def clear(self):
        for id in ['channel',
                   'genre0',
                   'genre00',
                   'genre01',
                   'genre02',
                   'genre03',
                   'genre04',
                   'genre05',
                   'genre06',
                   'genre07',
                   'genre08',
                   'genre09',
                   'genre10',
                   'genre11']:
            addon.setSetting(id, '')
        for id in ['keyword','query']:
            addon.setSetting(id, '')
        for id in ['source']:
            addon.setSetting(id, '0')

    def set(self, uname, squery):
        # リセット
        self.clear()
        # ダイアログに設定
        params = {'s':'', 'ch':'', 'genre0':'', 'genre1':''}
        for i in squery[1:].split('&'):
            key, value = i.split('=')
            params[key] = value
        # keyword
        addon.setSetting('keyword', uname)
        # source
        if params['s'] == 'e':
            addon.setSetting('source', '0')
        elif params['s'] == 'c':
            addon.setSetting('source', '1')
        # channel
        channel = Channel().search(params['ch'])
        addon.setSetting('channel',channel['name'])
        # genre
        genre = Genre().search(params['genre0'],params['genre1'])
        addon.setSetting('genre0',genre['name0'])
        addon.setSetting(genre['id'],genre['name1'])

    def edit(self, uname):
        # リセット
        self.clear()
        # スマートリスト設定を読み込む
        list = self.getList()
        # titleが一致するものをダイアログに設定
        for i in range(len(list)):
            if list[i]['title'] == uname:
                item = list[i]
                for key in item.keys():
                    addon.setSetting(key, item[key])
                break

    def add(self):
        # ダイアログの設定を取得
        source = addon.getSetting('source') # type(source)=str
        keyword = addon.getSetting('keyword') # type(keyword)=str
        # channel
        str2 = addon.getSetting('channel').decode('utf-8') # type(str2)=unicode
        channel = Channel().search(str2)
        # genre
        str0 = addon.getSetting('genre0').decode('utf-8') # type(str0)=unicode
        genre = Genre().search(str0)
        str1 = addon.getSetting(genre['id']).decode('utf-8') # type(str1)=unicode
        genre = Genre().search(str0, str1)
        # query
        query = 'n='+str(settings['apage'])+'&p=1&video=all'
        query += '&key='+urllib.quote(keyword)
        query += '&s='+['e','c'][int(source)]
        query += '&ch='+channel['id']
        query += '&genre0='+genre['id0']
        query += '&genre1='+genre['id1']
        # 既存のスマートリスト設定
        list = self.getList()
        # 既存のスマートリスト設定でqueryが一致するものを削除
        edited_query = addon.getSetting('query')
        for i in range(len(list)):
            if list[i]['query'] == edited_query:
                del list[i]
                break
        # データを追加
        data = {}
        data['title'] = keyword
        data['query'] = query
        data['channel'] = str2
        data['source'] = source
        data['keyword'] = keyword
        if genre['id0']: data['genre0'] = str0
        if genre['id1']: data[genre['id']] = str1
        list.append(data)
        # ファイルに書き込む
        self.setList(list)

    def delete(self, uname):
        list = self.getList()
        for i in range(len(list)):
            if list[i]['title'] == uname:
                del list[i]
                break
        self.setList(list)
