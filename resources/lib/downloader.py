# -*- coding: utf-8 -*-

import sys
import os
import json

from urllib.parse import urlencode

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


class Downloader:

    def __init__(self):
        self.local_addon = xbmcaddon.Addon()
        self.local_id = self.local_addon.getAddonInfo('id')
        try:
            self.remote_id = 'plugin.video.downloader'
            self.remote_addon = xbmcaddon.Addon(self.remote_id)
            self.download_path = self.remote_addon.getSetting('download_path')
            self.cache_path = os.path.join(xbmcvfs.translatePath(self.remote_addon.getAddonInfo('profile')), 'cache', self.local_id)
            if not os.path.isdir(self.cache_path):
                os.makedirs(self.cache_path)
        except Exception:
            self.remote_id = None
            self.remote_addon = None
            self.download_path = None
            self.cache_path = None

    def __available(self):
        return self.remote_addon is not None

    def __exists(self, contentid):
        filepath = os.path.join(self.download_path, self.local_id, '%s.mp4' % contentid)
        return os.path.isfile(filepath)

    def __jsonfile(self, contentid):
        return os.path.join(self.cache_path, '%s.json' % contentid)

    def __save(self, contentid, item):
        json_file = self.__jsonfile(contentid)
        if not os.path.isfile(json_file):
            with open(json_file, 'w', encoding='utf-8', errors='ignore') as f:
                json_data = json.dumps(item, indent=4, ensure_ascii=True, sort_keys=True)
                f.write(json_data)
        return json_file

    def top(self, iconimage=None):
        if self.__available():
            listitem = xbmcgui.ListItem(self.remote_addon.getLocalizedString(30927))
            listitem.setArt({'icon': iconimage})
            listitem.setInfo(type='video', infoLabels={})
            action = 'RunPlugin(plugin://%s?action=settings)' % (self.remote_id)
            contextmenu = [(self.remote_addon.getLocalizedString(30937), action)]
            listitem.addContextMenuItems(contextmenu, replaceItems=True)
            url = 'plugin://%s?action=list&addonid=%s' % (self.remote_id, self.local_id)
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, True)

    def contextmenu(self, item, url=None):
        contextmenu = []
        s = item['_summary']
        contentid = s['contentid']
        if self.__available():
            if self.__exists(contentid):
                args = {'action': 'delete', 'addonid': self.local_id, 'contentid': contentid}
                contextmenu = [(self.remote_addon.getLocalizedString(30930), 'RunPlugin(plugin://%s?%s)' % (self.remote_id, urlencode(args)))]
            else:
                json_file = self.__save(contentid, item)
                if url is None:
                    args = {'action': 'download', 'url': s['url'], 'contentid': contentid}
                    contextmenu = [(self.remote_addon.getLocalizedString(30929), 'RunPlugin(plugin://%s?%s)' % (self.local_id, urlencode(args)))]
                else:
                    args = {'action': 'add', 'addonid': self.local_id, 'url': url, 'json': json_file}
                    contextmenu = [(self.remote_addon.getLocalizedString(30929), 'RunPlugin(plugin://%s?%s)' % (self.remote_id, urlencode(args)))]
        return contextmenu

    def download(self, url, contentid):
        if self.__available():
            json_file = self.__jsonfile(contentid)
            args = {'action': 'add', 'addonid': self.local_id, 'url': url, 'json': json_file}
            xbmc.executebuiltin('RunPlugin(plugin://%s?%s)' % (self.remote_id, urlencode(args)))
