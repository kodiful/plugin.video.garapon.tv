# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, time
import re, os
import urllib, urllib2

from PIL import Image
from cStringIO import StringIO

try:
    from sqlite3 import dbapi2 as sqlite
except:
    from pysqlite2 import dbapi2 as sqlite

from common import(addon,settings)
from common import(DOWNLOAD_PATH,CACHE_PATH,CACHE_DB)

from channel import(Channel)
from genre import(Genre)


class Item:

    def __init__(self, item):
        self.item = item

    def title(self, onair=False):
        if onair:
            try:
                t = datetime.datetime.strptime(self.item['startdate'], '%Y-%m-%d %H:%M:%S')
            except TypeError:
                t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.item['startdate'],'%Y-%m-%d %H:%M:%S')))
            sdate = t.strftime('%H:%M')
            title = '[COLOR green]%s\u25b6[/COLOR] %s (%s〜)' % (self.item['bc'],self.item['title'],sdate)
        else:
            title = self.item['title']
        return title

    def duration(self, onair=False):
        if onair:
            duration = ''
        else:
            match = re.search('^([0-9]{2,}):([0-9]{2}):([0-9]{2})',self.item['duration'])
            duration = '%d' % (int(match.group(1))*60+int(match.group(2)))
        return duration

    def date(self):
        match = re.search('^([0-9]{4})-([0-9]{2})-([0-9]{2})',self.item['startdate'])
        date = '%s.%s.%s' % (match.group(3),match.group(2),match.group(1))
        return date

    def outline(self):
        outline = ''
        if self.item['description'] is None:
            return ''
        else:
            return ' ' + self.item['description']

    def plot(self):
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

    def studio(self):
        if self.item['bc'] is None:
            return ''
        else:
            return self.item['bc']

    def genre(self):
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

    def link(self):
        if settings['protocol'] == 'RTMP':
            link = 'rtmp://' + settings['addr']
            if settings['rtmp']:
                link += ':' + settings['rtmp']
            link += ' playpath=' + self.item['gtvid'] + '-' + settings['session']
        elif settings['protocol'] == 'RTMPT':
            link = 'rtmpt://' + settings['addr']
            if settings['http']:
                link += ':' + settings['http']
            link += ' playpath=' + self.item['gtvid'] + '-' + settings['session'] + '-' + settings['dev_id']
        elif settings['protocol'] == 'HLS':
            link = 'http://' + settings['addr']
            if settings['http']:
                link += ':' + settings['http']
            link += '/' + self.item['gtvid'] + '.m3u8?gtvsession=' + settings['session'] + '&starttime=0&dev_id=' + settings['dev_id']
        return link

    def thumbnail(self):
        imagefile = os.path.join(CACHE_PATH, self.item['gtvid']+'.png')
        if os.path.isfile(imagefile) and os.path.getsize(imagefile) < 1000:
            # delete imagefile
            os.remove(imagefile)
            # delete from database
            conn = sqlite.connect(CACHE_DB)
            c = conn.cursor()
            #c.execute("SELECT cachedurl FROM texture WHERE url = '%s';" % imagefile)
            c.execute("DELETE FROM texture WHERE url = '%s';" % imagefile)
            conn.commit()
            conn.close()
        if not os.path.isfile(imagefile):
            imageurl = 'http://' + settings['addr']
            if settings['http']:
                imageurl += ':' + settings['http']
            imageurl += '/thumbs/' + self.item['gtvid']
            buffer = urllib2.urlopen(imageurl).read() 
            image = Image.open(StringIO(buffer)) #320x180
            if settings['thumb'] == 'Crop':
                image = image.resize((384, 216))
                image = image.crop((84,0,300,216))
                image.save(imagefile, 'PNG')
            elif settings['thumb'] == 'Fit':
                image = image.resize((216, 122))
                background = Image.new('RGB', (216,216), (0,0,0))
                background.paste(image, (0,47))
                background.save(imagefile, 'PNG')
        return imagefile

    def contextmenu(self, sys):
        title = self.item['title'].encode('utf-8','ignore')
        menu = []
        # info
        menu.append((addon.getLocalizedString(30906), 'XBMC.Action(Info)'))
        # add smartlist
        try:
            if self.item['genre'][0]:
                genre = self.item['genre'][0].split('/')
            else:
                genre = ['','']
        except:
            genre = ['','']
        url1 = 'ch=%s&genre0=%s&genre1=%s' % (self.item['ch'], genre[0], genre[1])
        menu.append((addon.getLocalizedString(30903),
                     'XBMC.RunPlugin(%s?mode=61&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url1))))
        # favorite
        if settings['favorite'] == 'true':
            url2 = 'gtvid=%s&rank=1' % (self.item['gtvid'])
            url3 = 'gtvid=%s&rank=0' % (self.item['gtvid'])
            if self.item['favorite'] == '0':
                # add
                action = 'XBMC.RunPlugin(%s?mode=20&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url2))
                menu.append((addon.getLocalizedString(30925), action))
            else:
                # delete
                action = 'XBMC.RunPlugin(%s?mode=20&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url3))
                menu.append((addon.getLocalizedString(30926), action))
        # download
        if settings['download'] == 'true':
            url4 = 'gtvid=%s' % (self.item['gtvid'])
            json = os.path.join(DOWNLOAD_PATH, self.item['gtvid']+'.js')
            if os.path.isfile(json):
                # add
                action = 'XBMC.RunPlugin(%s?mode=31&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url4))
                menu.append((addon.getLocalizedString(30930), action))
            else:
                # delete
                action = 'XBMC.RunPlugin(%s?mode=30&name=%s&url=%s)' % (sys.argv[0],urllib.quote_plus(title),urllib.quote_plus(url4))
                menu.append((addon.getLocalizedString(30929), action))
        return menu


class Cache:

    def __init__(self):
        self.files = os.listdir(CACHE_PATH)

    def clear(self):
        for file in self.files:
            try: os.remove(os.path.join(CACHE_PATH, file))
            except: pass

    def update(self):
        size = 0
        for file in self.files:
            try: size = size + os.path.getsize(os.path.join(CACHE_PATH, file))
            except: pass
        if size > 1024*1024:
            addon.setSetting('cache', '%.1f MB / %d files' % (size/1024.0/1024.0,len(self.files)))
        elif size > 1024:
            addon.setSetting('cache', '%.1f kB / %d files' % (size/1024.0,len(self.files)))
        else:
            addon.setSetting('cache', '%d bytes / %d files' % (size,len(self.files)))

def query2desc(query):

    params = {'sdate':None, 'ch':None, 'genre0':None, 'genre1':None, 's':None}
    lines = []
    
    # parse query
    for q in query.split('&'):
        (key, value) = q.split('=')
        params[key] = value

    # date
    if params['sdate'] is None:
        pass
    elif params['sdate'] == '':
        lines.append('%s:%s' % (addon.getLocalizedString(30907),addon.getLocalizedString(30912))) #日付:すべての日付
    else:
        lines.append('%s:%s' % (addon.getLocalizedString(30907),str(params['sdate']).split(' ')[0])) #日付:*

    # channel
    if params['ch'] is None:
        pass
    elif params['ch'] == '':
        lines.append('%s:%s' % (addon.getLocalizedString(30908),addon.getLocalizedString(30913))) #チャンネル:すべてのチャンネル
    else:
        lines.append('%s:%s' % (addon.getLocalizedString(30908),Channel().search(params['ch'])['name'])) #チャンネル:*

    # genre
    if params['genre0'] is None:
        pass
    elif params['genre0'] == '':
        lines.append('%s:%s' % (addon.getLocalizedString(30909),addon.getLocalizedString(30914))) #ジャンル:すべてのジャンル
    else:
        # subgenre
        if params['genre1'] is None:
            pass
        elif params['genre1'] == '':
            lines.append('%s:%s' % (addon.getLocalizedString(30909),Genre().search(params['genre0'])['name0'])) #ジャンル:*
        else:
            lines.append('%s:%s' % (addon.getLocalizedString(30909),Genre().search(params['genre0'],params['genre1'])['name1'])) #ジャンル:*

    # search
    if params['s'] is None:
        pass
    elif params['s'] == 'e':
        lines.append('%s:%s' % (addon.getLocalizedString(30911),addon.getLocalizedString(30901))) #検索対象:EPG
    elif params['s'] == 'c':
        lines.append('%s:%s' % (addon.getLocalizedString(30911),addon.getLocalizedString(30902))) #検索対象:字幕

    # join lines
    return '\n'.join(lines)
