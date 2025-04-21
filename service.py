# -*- coding: utf-8 -*-

import os
import socket
import threading
import shutil
import json
from urllib.parse import parse_qs

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal
from resources.lib.service import Service


if __name__ == '__main__':

    # HTTP接続のタイムアウト(秒)を設定
    socket.setdefaulttimeout(60)

    # DBファイルの有無をチェック
    require_transfer = False
    if os.path.exists(Common.CONTENTS_DB) is False:
        # DBファイルがない場合はテンプレートをコピー
        require_transfer = True
        shutil.copyfile(Common.TEMPLATE_DB, Common.CONTENTS_DB)

    # DBインスタンスを作成
    ThreadLocal.db = db = DB()

    # DBファイルがない場合は既存データをインポート
    if require_transfer:
        Common.notify('Transferring data...')
        # バックアップフォルダを作成
        backup_dir = os.path.join(Common.PROFILE_PATH, '~backup')
        os.makedirs(backup_dir, exist_ok=True)
        # channel.jsをDBにインポート
        channel_file = os.path.join(Common.PROFILE_PATH, 'channel.js')
        if os.path.exists(channel_file):
            with open(channel_file) as f:
                data = json.loads(f.read())
                values = [(key, *value.values()) for key, value in data['ch_list'].items()]
                db.cursor.executemany('''INSERT INTO channels VALUES (?, ?, ?)''', values)
            shutil.move(channel_file, backup_dir)
        # smartlist.jsをDBにインポート
        smartlist_file = os.path.join(Common.PROFILE_PATH, 'smartlist.js')
        if os.path.exists(smartlist_file):
            with open(smartlist_file) as f:
                for item in json.loads(f.read()):
                    q = parse_qs(item['query'], keep_blank_values=True)
                    genre0 = q.get('g0') or q.get('genre0') or ['']
                    genre1 = q.get('g1') or q.get('genre1') or ['']
                    # channelを検索
                    if item['channel'].startswith('[COLOR'):
                        ch_name, ch_id = '', ''
                    else:
                        ch_name = item['channel']
                        sql = 'SELECT ch_id FROM channels WHERE ch_name = :ch_name'
                        db.cursor.execute(sql, {'ch_name': ch_name})
                        ch_id, = db.cursor.fetchone()
                    # genreを検索
                    sql = 'SELECT genre_name, subgenre_name FROM genres WHERE genre_id = :genre_id AND subgenre_id = :subgenre_id'
                    db.cursor.execute(sql, {'genre_id': genre0[0], 'subgenre_id': genre1[0]})
                    genre_name, subgenre_name = db.cursor.fetchone()
                    data = {
                        'ch_id': ch_id,
                        'ch_name': ch_id and ch_name,
                        'keyword': item['keyword'],
                        'source': {'0': 'e', '1': 'c'}[item['source']],
                        'genre_id': genre0[0],
                        'genre_name': genre0[0] and genre_name,
                        'subgenre_id': genre1[0],
                        'subgenre_name': genre1[0] and subgenre_name
                    }
                    columns = ','.join(data.keys())
                    placeholders = ','.join(['?' for _ in data.values()])
                    sql = f'INSERT INTO smartlist ({columns}) VALUES ({placeholders})'
                    db.cursor.execute(sql, list(data.values()))
            shutil.move(smartlist_file, backup_dir)
        # resume.jsをバックアップ
            shutil.move(os.path.join(Common.PROFILE_PATH, 'resume.js'), backup_dir)

    # サービスを初期化
    service = Service()
    # 別スレッドでサービスを起動
    thread = threading.Thread(target=service.monitor, daemon=True)
    thread.start()

    # DBインスタンスを終了
    ThreadLocal.db.conn.close()
    ThreadLocal.db = None
