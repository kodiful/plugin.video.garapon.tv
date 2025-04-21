# -*- coding: utf-8 -*-

from resources.lib.db import ThreadLocal


class Genre:

    def __init__(self):
        self.db = ThreadLocal.db

    def search(self, key0, key1=None):
        if key1 is None:
            sql = 'SELECT DISTINCT genre_id, genre_name FROM genres WHERE :key0 in (genre_id, genre_name)'
            self.db.cursor.execute(sql, {'key0': key0})
            genre_id, genre_name = self.db.cursor.fetchone()
            subgenre_id, subgenre_name = '', ''
        else:
            sql = '''SELECT DISTINCT genre_id, genre_name, subgenre_id, subgenre_name FROM genres
            WHERE :key0 in (genre_id, genre_name) AND :key1 in (subgenre_id, subgenre_name)'''
            self.db.cursor.execute(sql, {'key0': key0, 'key1': key1})
            genre_id, genre_name, subgenre_id, subgenre_name = self.db.cursor.fetchone()
        return {'genre_id': genre_id, 'genre_name': genre_name, 'subgenre_id': subgenre_id, 'subgenre_name': subgenre_name}

    def getDefault(self, id):
        self.db.cursor.execute('SELECT subgenre_name FROM genres WHERE genre_id = :genre_id and subgenre_id = ""', {'genre_id': id})
        subgenre_name, = self.db.cursor.fetchone()
        return subgenre_name
