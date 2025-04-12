# -*- coding: utf-8 -*-

import sqlite3
import locale

from resources.lib.common import Common


class Holiday(Common):

    def __init__(self, db_path):
        # ロケール設定（日付フォーマットのため）
        locale.setlocale(locale.LC_ALL, '')
        # DB初期化
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def is_holiday(self, date):
        sql = 'SELECT name FROM holidays WHERE date = :date'
        self.cursor.execute(sql, {'date': date})
        name = self.cursor.fetchone()
        return name

    def convert(self, timestamp, format, color=None):
        # timestamp: 2025-04-05 12:34:00
        # format: %Y年%m月%d日(%a) %H:%M
        # return: [COLOR blue]2025年04月05日(土) 12:34[/COLOR]
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
