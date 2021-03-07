# -*- coding: utf-8 -*-

from resources.lib.common import Common


class Channel():

    DEFAULT_NAME = '[COLOR lightgreen]%s[/COLOR]' % Common.STR(30913)  # すべてのチャンネル

    def __init__(self):
        self.data = Common.read_json(Common.CHANNEL_FILE)

    def search(self, key):
        result = {'id': '', 'name': '', 'hash': ''}
        for key, val in filter(lambda x: key in {x[0], x[1]['ch_name'], x[1]['hash_tag']}, self.data['ch_list'].items()):
            result['id'] = key
            result['name'] = val['ch_name']
            result['hash'] = val['hash_tag']
        return result

    def getList(self):
        result = [{'id': '', 'name': self.DEFAULT_NAME}]
        for key, value in self.data['ch_list'].items():
            result.append({'id': key, 'name': value['ch_name']})
        return sorted(result, key=lambda item: item['id'])

    def getLabel(self):
        return '|'.join(map(lambda x: x['name'], self.getList()))

    def getDefault(self):
        return self.DEFAULT_NAME
