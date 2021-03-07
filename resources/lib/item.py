# -*- coding: utf-8 -*-

import datetime
import time
import re
import os
import sys
import io

from urllib.parse import urlencode

from PIL import Image
from sqlite3 import dbapi2 as sqlite

from resources.lib.common import Common
from resources.lib.genre import Genre
from resources.lib.request import Request
from resources.lib.downloader import Downloader


class Item():

    def __init__(self, item, onair=False):
        # オンエアのステータス
        self.onair = onair
        # JSONオブジェクトをコピーする
        self.item = item
        # 付加情報で上書きする
        gtvid = self.item['gtvid']
        self.item['_summary'] = {
            'title': self.item['title'],
            'url': Request().content_url(gtvid),
            'date': self.item['startdate'],
            'description': self.item['description'],
            'source': self.item['bc'],
            'category': self.genre(),
            'duration': self.duration(),
            'thumbnail': Request().thumbnail_url(gtvid),
            'thumbfile': self.thumbnail(),
            'contentid': gtvid,
        }
        # コンテキストメニュー
        self.contextmenu = self.get_contextmenu()

    def title(self):
        if self.onair:
            try:
                t = datetime.datetime.strptime(self.item['startdate'], '%Y-%m-%d %H:%M:%S')
            except TypeError:
                t = datetime.datetime.fromtimestamp(time.mktime(time.strptime(self.item['startdate'], '%Y-%m-%d %H:%M:%S')))
            sdate = t.strftime('%H:%M')
            s = time.strptime(self.item['duration'], '%H:%M:%S')
            s = t + datetime.timedelta(hours=s.tm_hour, minutes=s.tm_min, seconds=s.tm_sec)
            edate = s.strftime('%H:%M')
            title = '%s [COLOR khaki]▶ %s (%s〜%s)[/COLOR]' % (self.item['bc'], self.item['title'], sdate, edate)
        else:
            title = self.item['title']
        return title

    def date(self):
        match = re.search('^([0-9]{4})-([0-9]{2})-([0-9]{2})', self.item['startdate'])
        date = '%s.%s.%s' % (match.group(3), match.group(2), match.group(1))
        return date

    def duration(self):
        if self.onair:
            duration = ''
        else:
            match = re.search('^([0-9]{2,}):([0-9]{2}):([0-9]{2})', self.item['duration'])
            duration = '%d' % (int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(2)))
        return duration

    def genre(self):
        if self.item['genre'] is None:
            return ''
        else:
            buf = []
            for item1 in self.item['genre']:
                (id0, id1) = item1.split('/')
                genre = Genre().search(id0, id1)
                if genre['name1']:
                    buf.append(genre['name1'])
                elif genre['name0']:
                    buf.append(genre['name0'])
            return ', '.join(buf)

    def thumbnail(self):
        imagefile = os.path.join(Common.CACHE_PATH, '%s.png' % self.item['gtvid'])
        if os.path.isfile(imagefile) and os.path.getsize(imagefile) < 1000:
            # delete imagefile
            os.remove(imagefile)
            # delete from database
            conn = sqlite.connect(Common.CACHE_DB)
            c = conn.cursor()
            # c.execute("SELECT cachedurl FROM texture WHERE url = '%s';" % imagefile)
            c.execute("DELETE FROM texture WHERE url = '%s';" % imagefile)
            conn.commit()
            conn.close()
        if os.path.isfile(imagefile):
            pass
        else:
            buffer = Request().thumbnail(gtvid=self.item['gtvid'])
            image = Image.open(io.BytesIO(buffer))  # 320x180
            image = image.resize((216, 122))
            background = Image.new('RGB', (216, 216), (0, 0, 0))
            background.paste(image, (0, 47))
            background.save(imagefile, 'PNG')
        return imagefile

    # コンテキストメニュー
    def get_contextmenu(self):
        gtvid = self.item['gtvid']
        title = self.item['title']
        menu = []
        # 詳細情報
        menu.append((Common.STR(30906), 'Action(Info)'))
        # スマートリストに追加
        try:
            if self.item['genre'][0]:
                genre = self.item['genre'][0].split('/')
            else:
                genre = ['', '']
        except Exception:
            genre = ['', '']
        args = {'mode': 'beginEditSmartList', 'name': title, 'ch': self.item['ch'], 'genre0': genre[0], 'genre1': genre[1]}
        menu.append((Common.STR(30903), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        # お気に入りに追加
        if self.item['favorite'] == '0':
            # add
            args = {'mode': 'switchFavorites', 'name': title, 'url': urlencode({'gtvid': gtvid, 'rank': 1})}
            menu.append((Common.STR(30925), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        else:
            # delete
            args = {'mode': 'switchFavorites', 'name': title, 'url': urlencode({'gtvid': gtvid, 'rank': 0})}
            menu.append((Common.STR(30926), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        # サウンロードに追加
        menu += Downloader().contextmenu(self.item, Request().content_url(gtvid))
        # トップに戻る
        menu.append((Common.STR(30936), 'Container.Update(%s,replace)' % (sys.argv[0])))
        return menu
