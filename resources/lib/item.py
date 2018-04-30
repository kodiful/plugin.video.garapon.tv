# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, time
import re, os, sys
import urllib

from PIL import Image
from cStringIO import StringIO

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from channel import Channel
from genre import Genre
from const import Const
from request import Request

#-------------------------------------------------------------------------------
class Item():

    def __init__(self, item, onair=False):
        # JSONオブジェクトを格納する
        self.item = item
        # プロパティを抽出する
        self.title       = self.get_title(onair)
        self.duration    = self.get_duration(onair)
        self.date        = self.get_date()
        self.outline     = self.get_outline()
        self.plot        = self.get_plot()
        self.studio      = self.get_studio()
        self.genre       = self.get_genre()
        self.link        = self.get_link()
        self.thumbnail   = self.get_thumbnail()
        self.contextmenu = self.get_contextmenu()

    def get_title(self, onair=False):
        if onair:
            try:
                t = datetime.datetime.strptime(self.item['startdate'],'%Y-%m-%d %H:%M:%S')
            except TypeError:
                t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.item['startdate'],'%Y-%m-%d %H:%M:%S')))
            sdate = t.strftime('%H:%M')
            s = time.strptime(self.item['duration'],'%H:%M:%S')
            s = t + datetime.timedelta(hours=s.tm_hour, minutes=s.tm_min, seconds=s.tm_sec)
            edate = s.strftime('%H:%M')
            title = '[COLOR green]%s\u25b6[/COLOR] %s (%s〜%s)' % (self.item['bc'],self.item['title'],sdate,edate)
        else:
            title = self.item['title']
        return title

    def get_duration(self, onair=False):
        if onair:
            duration = ''
        else:
            match = re.search('^([0-9]{2,}):([0-9]{2}):([0-9]{2})',self.item['duration'])
            #duration = '%d' % (int(match.group(1))*60+int(match.group(2)))
            duration = '%d' % (int(match.group(1))*3600+int(match.group(2))*60+int(match.group(2)))
        return duration

    def get_date(self):
        match = re.search('^([0-9]{4})-([0-9]{2})-([0-9]{2})',self.item['startdate'])
        date = '%s.%s.%s' % (match.group(3),match.group(2),match.group(1))
        return date

    def get_outline(self):
        outline = ''
        if self.item['description'] is None:
            return ''
        else:
            return ' ' + self.item['description']

    def get_plot(self):
        plot = self.item['startdate']
        if not self.item['description'] is None:
            plot += '\n' + self.item['description']
        try:
            hit = self.item['caption_hit']
            if int(hit) > 0:
                for i in range(int(hit)):
                    caption = self.item['caption'][i]
                    plot += '\n(%s) %s' % (caption['caption_time'],caption['caption_text'])
        except:
            pass
        return plot

    def get_studio(self):
        if self.item['bc'] is None:
            return ''
        else:
            return self.item['bc']

    def get_genre(self):
        if self.item['genre'] is None:
            return ''
        else:
            buf = []
            for item1 in self.item['genre']:
                (id0,id1) = item1.split('/')
                genre = Genre().search(id0,id1)
                if genre['name1']:
                    buf.append(genre['name1'])
                elif genre['name0']:
                    buf.append(genre['name0'])
            return ', '.join(buf)

    def get_link(self):
        return Request().content_url(gtvid=self.item['gtvid'])

    def get_thumbnail(self):
        imagefile = os.path.join(Const.CACHE_PATH, '%s.png' % self.item['gtvid'])
        if os.path.isfile(imagefile) and os.path.getsize(imagefile) < 1000:
            # delete imagefile
            os.remove(imagefile)
            # delete from database
            conn = sqlite.connect(Const.CACHE_DB)
            c = conn.cursor()
            #c.execute("SELECT cachedurl FROM texture WHERE url = '%s';" % imagefile)
            c.execute("DELETE FROM texture WHERE url = '%s';" % imagefile)
            conn.commit()
            conn.close()
        if not os.path.isfile(imagefile):
            buffer = Request().thumbnail(gtvid=self.item['gtvid'])
            image = Image.open(StringIO(buffer)) #320x180
            image = image.resize((216, 122))
            background = Image.new('RGB', (216,216), (0,0,0))
            background.paste(image, (0,47))
            background.save(imagefile, 'PNG')
        return imagefile

    def get_contextmenu(self):
        title = self.item['title'].encode('utf-8','ignore')
        menu = []
        # info
        action = 'Action(Info)'
        menu.append((Const.STR(30906), action))
        # add smartlist
        try:
            if self.item['genre'][0]:
                genre = self.item['genre'][0].split('/')
            else:
                genre = ['','']
        except:
            genre = ['','']
        url1 = 'ch=%s&genre0=%s&genre1=%s' % (self.item['ch'], genre[0], genre[1])
        action = 'RunPlugin(%s?mode=61&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url1))
        menu.append((Const.STR(30903), action))
        # favorite
        url2 = 'gtvid=%s&rank=1' % (self.item['gtvid'])
        url3 = 'gtvid=%s&rank=0' % (self.item['gtvid'])
        if self.item['favorite'] == '0':
            # add
            action = 'RunPlugin(%s?mode=20&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url2))
            menu.append((Const.STR(30925), action))
        else:
            # delete
            action = 'RunPlugin(%s?mode=20&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url3))
            menu.append((Const.STR(30926), action))
        # download
        if Const.PLUS_ADDON:
            url4 = 'gtvid=%s' % (self.item['gtvid'])
            json = os.path.join(Const.DOWNLOAD_PATH, self.item['gtvid']+'.js')
            if os.path.isfile(json):
                # delete
                action = 'RunPlugin(plugin://%s?action=delete&gtvid=%s)' % (Const.PLUS_ADDON_ID,urllib.quote_plus(self.item['gtvid']))
                menu.append((Const.PLUS_ADDON.getLocalizedString(30930), action))
            else:
                # add
                action = 'RunPlugin(plugin://%s?action=add&gtvid=%s)' % (Const.PLUS_ADDON_ID,urllib.quote_plus(self.item['gtvid']))
                menu.append((Const.PLUS_ADDON.getLocalizedString(30929), action))
        # return to top
        action = 'Container.Update(plugin://%s,replace)' % Const.ADDON_ID
        menu.append((Const.STR(30936), action))
        return menu

#-------------------------------------------------------------------------------
class Cache():

    def __init__(self):
        self.files = os.listdir(Const.CACHE_PATH)

    def clear(self):
        for file in self.files:
            try: os.remove(os.path.join(Const.CACHE_PATH, file))
            except: pass

    def update(self):
        size = 0
        for file in self.files:
            try: size = size + os.path.getsize(os.path.join(Const.CACHE_PATH, file))
            except: pass
        if size > 1024*1024:
            Const.SET('cache', '%.1f MB / %d files' % (size/1024.0/1024.0,len(self.files)))
        elif size > 1024:
            Const.SET('cache', '%.1f kB / %d files' % (size/1024.0,len(self.files)))
        else:
            Const.SET('cache', '%d bytes / %d files' % (size,len(self.files)))
