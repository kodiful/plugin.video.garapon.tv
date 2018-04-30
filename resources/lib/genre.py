# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import codecs
import json

from const import Const

#-------------------------------------------------------------------------------
class Genre():

    def __init__(self):
        if os.path.isfile(Const.GENRE_FILE):
            f = codecs.open(Const.GENRE_FILE,'r','utf-8')
            self.data = json.loads(f.read())
            f.close()

    def search(self, key0, key1=''):
        result = {'id':'','id0':'','name0':'','id1':'','name1':''}
        # 大分類リスト
        genre0_list = self.data
        for genre0 in genre0_list:
            try:
                result['id'] = genre0['id']
                g0 = genre0['genre0']
                # 大分類の番号
                id0 = g0['value']
                # 大分類の記述
                name0 = g0['name']
                # 配下の中分類リスト
                genre1_list = genre0['genre1']
                # 大分類の番号もしくは記述が一致
                if key0 == id0 or key0 == name0:
                    result['id0'] = id0
                    result['name0'] = name0
                    if key1:
                        for g1 in genre1_list:
                            # 中分類の番号
                            id1 = g1['value']
                            # 中分類の記述
                            name1 = g1['name']
                            # 中分類の番号もしくは記述が一致
                            if key1 == id1 or key1 == name1:
                                result['id1'] = id1
                                result['name1'] = name1
                                break
                    break
            except:
                pass
        return result

    def getData(self):
        return self.data

    def getList(self, id=None):
        data = []
        genre0_list = self.data
        if id is None:
            for genre0 in genre0_list:
                g0 = genre0['genre0']
                data.append({'id':g0['value'],'name':g0['name']})
        else:
            for genre0 in genre0_list:
                g0 = genre0['genre0']
                if id == g0['value']:
                    genre1_list = genre0['genre1']
                    for g1 in genre1_list:
                        data.append({'id':g1['value'],'name':g1['name']})
        return data

    def getLabel(self):
        data = {}
        # genre0
        list = []
        genre0_list = self.data
        for genre0 in genre0_list:
            g0 = genre0['genre0']
            list.append(g0['name'])
        data['genre0'] = '|'.join(list)
        # genre1
        for genre0 in genre0_list:
            try:
                id = genre0['id']
                list = []
                genre1_list = genre0['genre1']
                for g1 in genre1_list:
                    list.append(g1['name'])
                data[id] = '|'.join(list)
            except:
                pass
        return data
