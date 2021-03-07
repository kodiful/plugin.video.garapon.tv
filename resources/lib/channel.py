# -*- coding: utf-8 -*-

from resources.lib.common import Common


class Channel():

    def __init__(self):
        self.data = Common.read_json(Common.CHANNEL_FILE)

    def search(self, key):
        result = {'id': '', 'name': '', 'hash': ''}
        list = self.data['ch_list']
        for ch_id in list:
            ch_data = list[ch_id]
            ch_name = ch_data['ch_name']
            hash_tag = ch_data['hash_tag']
            if key == ch_id or key == ch_name or key == hash_tag:
                result['id'] = ch_id
                result['name'] = ch_name
                result['hash'] = hash_tag
                break
        return result

    def setData(self, data):
        Common.write_json(Common.CHANNEL_FILE, data)

    def getData(self):
        return self.data

    def getList(self):
        data = [{'id': '', 'name': '[COLOR lightgreen]%s[/COLOR]' % Common.STR(30913)}]  # すべてのチャンネル
        for key, value in self.data['ch_list'].items():
            data.append({'id': key, 'name': value['ch_name']})
        return sorted(data, key=lambda item: item['id'])

    def getLabel(self):
        list = []
        for c in self.getList():
            list.append(c['name'])
        return '|'.join(list)
