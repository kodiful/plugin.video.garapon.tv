# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import xbmc
import xbmcaddon
import os
import json


class Resume():
    
    def __init__(self, addon_id):
        # 初期設定
        self.resume = {}
        # アドオン
        self.addon = xbmcaddon.Addon(addon_id)
        # ファイルパス
        profile_path = xbmc.translatePath(self.addon.getAddonInfo('profile').decode('utf-8'))
        self.filepath = os.path.join(profile_path, 'resume')
        # 設定読み込み
        if os.path.isfile(self.filepath):
            f = open(self.filepath, 'r')
            self.resume = json.loads(f.read())
            f.close()
        else:
            self.resume = {}

    def update(self):
        f = open(self.filepath, 'w')
        f.write(json.dumps(self.resume))
        f.close()

    def get(self, key, default_value=None):
        try:
            value = self.resume[key]
        except KeyError:
            value = default_value
            if value is None:
                raise
            else:
                self.set(key, value)
        return value

    def set(self, key, value):
        self.resume[key] = value
        self.update()
        return value
