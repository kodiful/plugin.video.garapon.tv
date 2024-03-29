# -*- coding: utf-8 -*-

from resources.lib.common import Common


class Genre():

    def __init__(self):
        self.data = Common.read_json(Common.GENRE_FILE)

    def search(self, key0, key1=''):
        # 結果を格納するオブジェクト
        result = {'id': '', 'id0': '', 'name0': '', 'id1': '', 'name1': ''}
        # 大分類を検索
        for genre0 in filter(lambda x: key0 in {x['value'], x['name']}, self.data):
            result['id'] = genre0['id']
            result['id0'] = genre0['value']
            result['name0'] = genre0['name']
            # key1が指定されていたら
            if key1:
                # 中分類も検索
                for genre1 in filter(lambda x: key1 in {x['value'], x['name']}, genre0['g1']):
                    result['id1'] = genre1['value']
                    result['name1'] = genre1['name']
        return result

    def getList(self, id=None):
        result = []
        if id is None:
            # idの指定がない場合は大分類のリスト
            for genre0 in self.data:
                result.append({'id': genre0['value'], 'name': genre0['name']})
        else:
            # idで指定された大分類配下の中分類のリスト
            for genre0 in filter(lambda x: id == x['value'], self.data):
                for genre1 in genre0['g1']:
                    result.append({'id': genre1['value'], 'name': genre1['name']})
        return result

    def getLabel(self):
        result = {}
        # 大分類/中分類のリスト
        for genre0 in self.data:
            id = genre0['id']
            result[id] = '|'.join(map(lambda x: x['name'], genre0['g1']))
        return result

    def getDefault(self, id):
        return list(filter(lambda x: id == x['id'], self.data))[0]['g1'][0]['name']
