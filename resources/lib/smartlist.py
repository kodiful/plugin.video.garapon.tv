# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import codecs
import urllib, urlparse
import json

from common import *
from channel import Channel
from genre import Genre
from const import Const

#-------------------------------------------------------------------------------
class SmartList():

    def __init__(self):
        return

    def getList(self):
        if os.path.exists(Const.SMARTLIST_FILE):
            try:
                f = codecs.open(Const.SMARTLIST_FILE,'r','utf-8')
                list = json.loads(f.read())
                f.close()
            except:
                list = []
        else:
            list = []
        return list

    def setList(self, list):
        # queryでソート
        list = sorted(list, key=lambda item: item['query'])
        # ファイルに書き込む
        f = codecs.open(Const.SMARTLIST_FILE,'w','utf-8')
        #f.write(json.dumps(list))
        f.write(json.dumps(list, sort_keys=True, ensure_ascii=False, indent=2))
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
            Const.SET(id, '')
        for id in ['keyword','query']:
            Const.SET(id, '')
        for id in ['source']:
            Const.SET(id, '0')

    def set(self, uname, query):
        # リセット
        self.clear()
        # ダイアログに設定
        args = urlparse.parse_qs(query, keep_blank_values=True)
        for key in args.keys(): args[key] = args[key][0]
        # keyword
        Const.SET('keyword', uname)
        # source
        s = args.get('s','')
        if s == 'e':
            Const.SET('source', '0')
        elif s == 'c':
            Const.SET('source', '1')
        # channel
        ch = args.get('ch','')
        channel = Channel().search(ch)
        Const.SET('channel',channel['name'])
        # genre
        genre0 = args.get('genre0','')
        genre1 = args.get('genre1','')
        genre = Genre().search(genre0, genre1)
        Const.SET('genre0',genre['name0'])
        Const.SET(genre['id'],genre['name1'])

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
                    Const.SET(key, item[key])
                break

    def add(self):
        # ダイアログの設定を取得
        source = Const.GET('source') # type(source)=str
        keyword = Const.GET('keyword') # type(keyword)=str
        # channel
        str2 = Const.GET('channel').decode('utf-8') # type(str2)=unicode
        channel = Channel().search(str2)
        # genre
        str0 = Const.GET('genre0').decode('utf-8') # type(str0)=unicode
        genre = Genre().search(str0)
        str1 = Const.GET(genre['id']).decode('utf-8') # type(str1)=unicode
        genre = Genre().search(str0, str1)
        # query
        query = 'n='+str(Const.ITEMS)+'&p=1&video=all'
        query += '&key='+urllib.quote(keyword)
        query += '&s='+['e','c'][int(source)]
        query += '&ch='+channel['id']
        query += '&genre0='+genre['id0']
        query += '&genre1='+genre['id1']
        # 既存のスマートリスト設定
        list = self.getList()
        # 既存のスマートリスト設定でqueryが一致するものを削除
        edited_query = Const.GET('query')
        for i in range(len(list)):
            if list[i]['query'] == edited_query:
                del list[i]
                break
        # データを追加
        data = {}
        data['title'] = keyword.decode('utf-8')
        data['query'] = query
        data['channel'] = str2
        data['source'] = source.decode('utf-8')
        data['keyword'] = keyword.decode('utf-8')
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
