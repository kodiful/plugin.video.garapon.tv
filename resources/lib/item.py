# -*- coding: utf-8 -*-

import os
import sys
import io
import json
from datetime import timedelta
from urllib.parse import urlencode
from PIL import Image
from sqlite3 import dbapi2 as sqlite

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.request import Request
from resources.lib.downloader import Downloader


class Item(Common):

    def __init__(self, item, onair=False):
        self.db = ThreadLocal.db
        self.item = item
        self.onair = onair

    @property
    def gtvid(self):
        return self.item['gtvid']

    @property
    def title(self):
        return self.item['title']

    @property
    def bc(self):
        return self.item['bc']

    @property
    def ch(self):
        return self.item['ch']
        
    @property
    def startdate(self):
        return self.item['startdate']
    
    @property
    def description(self):
        return self.item['description']

    @property
    def summary(self):
        return {
            'title': self.title,
            'url': self.content_url,
            'date': self.startdate,
            'description': self.description,
            'source': self.bc,
            'category': self.genre,
            'duration': self.duration,
            'thumbnail': self.thumbnail_url,
            'thumbfile': self.thumbnail_file,
            'contentid': self.gtvid
        }
    
    @property
    def infolabels(self):
        return {
            'title': self.title,
            'plot': '%s\n%s' % (self.startdate, self.description),
            'plotoutline': self.description,
            'studio': self.bc,
            'genre': self.genre,
            'dateadded': self.startdate,
            'duration': self.duration,
        }
    
    @property
    def art(self):
        return {
            'icon': self.thumbnail_file,
            'thumb': self.thumbnail_file,
            'poster': self.thumbnail_file
        }
    
    @property
    def smartlist(self):
        # チャンネル情報を取得
        sql = 'SELECT ch_id, ch_name FROM channels WHERE ch_name = :ch_name'
        self.db.cursor.execute(sql, {'ch_name': self.item['bc']})
        ch_id, ch_name = self.db.cursor.fetchone()
        # ジャンル情報を取得
        genre_id, subgenre_id = json.loads(self.item['genre'])[0].split('/')
        sql = 'SELECT genre_name, subgenre_name FROM genres WHERE genre_id = :genre_id AND subgenre_id = :subgenre_id'
        self.db.cursor.execute(sql, {'genre_id': genre_id, 'subgenre_id': subgenre_id})
        genre_name, subgenre_name = self.db.cursor.fetchone()
        # スマートリスト情報を返す
        return {
            'name': self.title,
            'ch_id': ch_id,
            'ch_name': ch_id and ch_name,
            'keyword': self.title,
            'source': 'e',
            'genre_id': genre_id,
            'genre_name': genre_id and genre_name,
            'subgenre_id': subgenre_id,
            'subgenre_name': subgenre_id and subgenre_name
        }
    
    @property
    def label(self):
        sdate = self.datetime(self.startdate).strftime('%H:%M')
        h, m, s = self.item['duration'].split(':')
        duration = timedelta(hours=int(h), minutes=int(m), seconds=int(s)).total_seconds()
        edate = (self.datetime(self.startdate) + timedelta(seconds=duration)).strftime('%H:%M')
        if self.onair:
            title = '%s [COLOR khaki]▶ %s[/COLOR]' % ('%s〜%s [COLOR lightgreen]▶ %s[/COLOR]' % (sdate, edate, self.bc), self.title)
        else:
            title = '%s [COLOR khaki]▶ %s[/COLOR]' % (self.db.convert(self.startdate, '%s %s〜%s' % (self.STR(30919), sdate, edate)), self.title)
        return title

    @property
    def duration(self):
        h, m, s = self.item['duration'].split(':')
        return timedelta(hours=int(h), minutes=int(m), seconds=int(s)).total_seconds()

    @property
    def genre(self):
        buf = []
        for genre in json.loads(self.item['genre']):
            self.log(genre)
            id0, id1 = genre.split('/')
            sql = 'SELECT genre_name, subgenre_name FROM genres WHERE genre_id = :id0 AND subgenre_id = :id1'
            self.db.cursor.execute(sql, {'id0': id0, 'id1': id1})
            name0, name1 = self.db.cursor.fetchone()
            buf.append(f'{name0}/{name1}')
        return ', '.join(buf)

    @property
    def contextmenu(self):
        contextmenu = []
        # 詳細情報
        contextmenu.append((Common.STR(30906), 'Action(Info)'))
        # スマートリストに追加
        args = {'action': 'editSmartlist', 'gtvid': self.gtvid}
        contextmenu.append((Common.STR(30903), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        # お気に入りに追加
        if self.item['favorite'] == '0':
            args = {'action': 'setFavorites', 'gtvid': self.gtvid, 'rank': 1}  # add
            contextmenu.append((Common.STR(30925), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        else:
            args = {'action': 'setFavorites', 'gtvid': self.gtvid, 'rank': 0}  # delete
            contextmenu.append((Common.STR(30926), 'RunPlugin(%s?%s)' % (sys.argv[0], urlencode(args))))
        # ダウンロードに追加
        contextmenu += Downloader().contextmenu(self.summary)
        # トップに戻る
        contextmenu.append((Common.STR(30936), 'Container.Update(%s,replace)' % (sys.argv[0])))
        return contextmenu

    @property
    def thumbnail_file(self):
        imagefile = os.path.join(Common.CACHE_PATH, '%s.png' % self.gtvid)
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
            buffer = Request().thumbnail(gtvid=self.gtvid)
            image = Image.open(io.BytesIO(buffer))  # 320x180
            image = image.resize((216, 122))
            background = Image.new('RGB', (216, 216), (0, 0, 0))
            background.paste(image, (0, 47))
            background.save(imagefile, 'PNG')
        return imagefile
    
    @property
    def content_url(self):
        return Request().content_url(self.gtvid)

    @property
    def thumbnail_url(self):
        return Request().thumbnail_url(self.gtvid)
