# -*- coding: utf-8 -*-

import locale
import sqlite3
import threading
import json
from datetime import datetime, timezone, timedelta

from resources.lib.common import Common


# DBの共有インスタンスを格納するスレッドローカルデータ
ThreadLocal = threading.local()


class DB(Common):

    sql_contents = '''
    CREATE TABLE IF NOT EXISTS contents(
        gtvid TEXT PRIMARY KEY,     -- '1SJP7FE21744533000'
        startdate TEXT,             -- '2025-04-13 17:30:00'
        duration TEXT,              -- '00:30:00'
        ch TEXT,                    -- '32738'
        title TEXT,                 -- '笑点[解][字]阿佐ヶ谷姉妹がテーマパークをネタに爆笑漫才！好楽がパンツの秘密を暴露！？',
        description TEXT,           -- '阿佐ヶ谷姉妹の漫才！おばさんの特徴を活かしたネタに会場大爆笑！大喜利は、冷静さを失った昇太がとった驚きの行動に、一之輔が見事な逆襲！小遊三は自分の○○を忘れる!?',
        favorite TEXT,              -- '0',
        audio_ch TEXT,              -- '0',
        seq_genregtvid_tbl TEXT,    -- '4165290',
        genre1 TEXT,                -- '9',
        genre2 TEXT,                -- '3',
        genre TEXT,                 -- '["9/3", "5/3"]'
        bc TEXT,                    -- '日テレ',
        bc_tags TEXT,               -- '#ntv',
        ts TEXT                     -- '1'
    )'''

    sql_smartlist = '''
    CREATE TABLE IF NOT EXISTS smartlist(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ch_id TEXT,
        ch_name TEXT,
        keyword TEXT,
        source TEXT,
        genre_id TEXT,
        genre_name TEXT,
        subgenre_id TEXT,
        subgenre_name TEXT
    )'''

    sql_channels = '''
    CREATE TABLE IF NOT EXISTS channels(
        ch_id TEXT PRIMARY KEY,     -- '32736'
        ch_name TEXT,               -- 'ＮＨＫ総合 東京'
        hash_tag TEXT               -- '#nhk'
    )'''

    sql_genres = '''
    CREATE TABLE IF NOT EXISTS genres(
        genre_id TEXT,
        genre_name TEXT,
        subgenre_id TEXT,
        subgenre_name TEXT
    )'''

    sql_cities = '''
    CREATE TABLE IF NOT EXISTS cities(
        code TEXT,
        region TEXT,
        pref TEXT,
        city TEXT,
        area_id TEXT
    )'''

    sql_holidays = '''
    CREATE TABLE IF NOT EXISTS holidays(
        date TEXT,
        name TEXT
    )'''

    def __init__(self):
        # ロケール設定（日付フォーマットのため）
        locale.setlocale(locale.LC_ALL, '')
        # DBへ接続
        #self.conn = sqlite3.connect(self.CONTENTS_DB, isolation_level=None)
        self.conn = sqlite3.connect(self.CONTENTS_DB, isolation_level=None, check_same_thread=False)  # add option for windows
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # テーブルを初期化
        self.cursor.execute(self.sql_contents)
        self.cursor.execute(self.sql_smartlist)
        self.cursor.execute(self.sql_channels)
        self.cursor.execute(self.sql_genres)
        self.cursor.execute(self.sql_cities)
        self.cursor.execute(self.sql_holidays)
        # 現在時刻取得関数
        def now():
            jst = timezone(timedelta(hours=9))
            return datetime.now(timezone.utc).astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
        self.conn.create_function('NOW', 0, now)
        # epoch時間変換関数
        def epoch(time_str):
            dt = self.datetime(time_str)
            return int(dt.timestamp())
        self.conn.create_function('EPOCH', 1, epoch)

    # 番組情報追加
    def add(self, data):
        '''
        {
            "gtvid": "1SJP7FE21744533000",
            "startdate": "2025-04-13 17:30:00",
            "duration": "00:30:00",
            "ch": "32738",
            "title": "笑点[解][字]阿佐ヶ谷姉妹がテーマパークをネタに爆笑漫才！好楽がパンツの秘密を暴露！？",
            "description": "阿佐ヶ谷姉妹の漫才！おばさんの特徴を活かしたネタに会場大爆笑！大喜利は、冷静さを失った昇太がとった驚きの行動に、一之輔が見事な逆襲！小遊三は自分の○○を忘れる!?",
            "favorite": "0",
            "audio_ch": "0",
            "seq_genregtvid_tbl": "4165290",
            "genre1": "9",
            "genre2": "3",
            "genre": [
                "9/3",
                "5/3"
            ],
            "bc": "日テレ",
            "bc_tags": "#ntv",
            "ts": 1
        }
        '''
        # DBに追加
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f'INSERT OR REPLACE INTO contents ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(map(lambda x: json.dumps(x) if isinstance(x, list) else str(x), data.values())))

    # 祝祭日判定
    def is_holiday(self, date):
        sql = 'SELECT name FROM holidays WHERE date = :date'
        self.cursor.execute(sql, {'date': date})
        name = self.cursor.fetchone()
        return name

    # 日付フォーマット
    def convert(self, timestamp, format, color=None):
        # timestamp: "2025-04-05 12:34:00"
        # format: "%Y年%m月%d日(%a) %H:%M"
        # return: "[COLOR blue]2025年04月05日(土) 12:34[/COLOR]"
        text = self.datetime(timestamp).strftime(format)
        w = self.weekday(timestamp)
        if color:
            text = f'[COLOR {color}]{text}[/COLOR]'
        elif self.is_holiday(timestamp[:10]):  # 祝祭日
            text = f'[COLOR red]{text}[/COLOR]'
        elif w == 6:  # 日曜日
            text = f'[COLOR red]{text}[/COLOR]'
        elif w == 5:  # 土曜日
            text = f'[COLOR blue]{text}[/COLOR]'
        return text

