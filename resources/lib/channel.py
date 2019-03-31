# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import codecs
import json

from const import Const

#-------------------------------------------------------------------------------
class Channel():

    def __init__(self):
        if os.path.isfile(Const.CHANNEL_FILE):
            f = codecs.open(Const.CHANNEL_FILE,'r','utf-8')
            self.data = json.loads(f.read())
            f.close()

    def search(self, key):
        result = {'id':'', 'name':'', 'hash':''}
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
        f = codecs.open(Const.CHANNEL_FILE,'w','utf-8')
        f.write(json.dumps(data))
        f.close()

    def getData(self):
        return self.data

    def getList(self):
        data = [{'id':'', 'name':'[COLOR green]%s[/COLOR]' % (Const.STR(30913))}] #すべてのチャンネル
        for key, value in self.data['ch_list'].iteritems():
            data.append({'id':key, 'name':value['ch_name']})
        return sorted(data, key=lambda item: item['id'])

    def getLabel(self):
        list = []
        for c in self.getList():
            list.append(c['name'])
        return '|'.join(list)
