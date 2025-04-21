# -*- coding: utf-8 -*-

from resources.lib.db import ThreadLocal


class Channel:

    def __init__(self):
        self.db = ThreadLocal.db

    def search(self, key):
        sql = 'SELECT ch_id, ch_name, hash_tag FROM channels WHERE :key in (ch_id, ch_name, hash_tag)'
        self.db.cursor.execute(sql, {'key': key})
        result = self.db.cursor.fetchone()
        return result

    def getDefault(self):
        self.db.cursor.execute('SELECT ch_name FROM channels WHERE ch_id = ""')
        ch_name, = self.db.cursor.fetchone()
        return ch_name
