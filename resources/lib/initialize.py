# -*- coding: utf-8 -*-

import os
import shutil
import json

from resources.lib.common import Common
from resources.lib.db import ThreadLocal
from resources.lib.channel import Channel
from resources.lib.genre import Genre
from resources.lib.request import Request


def initializeNetwork():
    # リセット
    Common.SET('garapon_addr', '')
    Common.SET('garapon_http', '0')
    Common.SET('garapon_https', '0')
    # データ取得
    response_body = Request().getgtvaddress()
    if response_body:
        params = {}
        for i in response_body.split('\n'):
            try:
                (key, value) = i.split(';', 1)
                if key == '0':
                    params['message'] = value
                elif key == '1':
                    params['message'] = value
                else:
                    params[key] = value
            except Exception:
                pass
        if params['message'] == 'success':
            Common.SET('garapon_addr', params['ipaddr'])
            if params['ipaddr'] == params['gipaddr']:
                Common.SET('garapon_http', params['port'])
                Common.SET('garapon_https', params['port2'])
            Common.notify('Network initialized successfully')
            return True
        else:
            Common.log('getgtvaddress failed', response_body, error=True)
            Common.notify('Network initialization failed')
            return False
    else:
        Common.log('empty response', error=True)
        Common.notify('Network initialization failed')
        return False


def initializeSession():
    # リセット
    Common.SET('garapon_session', '')
    # データ取得
    response_body = Request().auth()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            if response_data['login'] == 1:
                gtvsession = response_data['gtvsession']
                Common.SET('garapon_session', gtvsession)
                Common.notify('Session initialized successfully')
                return True
            else:
                Common.log('auth failed', response_body, error=True)
                Common.notify('Session initialization failed')
                return False
        else:
            Common.log('auth failed', response_body, error=True)
            Common.notify('Session initialization failed')
            return False
    else:
        Common.log('empty response', error=True)
        Common.notify('Session initialization failed')
        return False


def initializeChannel():
    # DB
    db = ThreadLocal.db
    # リセット
    Common.SET('garapon_ch', '')
    db.cursor.execute('DELETE FROM channels WHERE ch_id != ""')
    # チャンネル情報を取得
    response_body = Request().channel()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            # チャンネル情報をDBに格納
            values = []
            for key, value in response_data['ch_list'].items():
                values.append((key, value['ch_name'], value['hash_tag']))
            db.cursor.executemany('''INSERT INTO channels VALUES (?, ?, ?)''', values)
            # チャンネル数を設定
            Common.SET('garapon_ch', '%d channels' % len(response_data['ch_list'].keys()))
            # 設定画面のテンプレートを読み込む
            with open(Common.TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                template = f.read()
            # テンプレートに書き出すチャンネル情報
            sql = '''SELECT GROUP_CONCAT(ch_name, '|') FROM channels
            ORDER BY ch_id'''
            db.cursor.execute(sql)
            channels, = db.cursor.fetchone()
            # テンプレートに書き出すジャンル情報
            sql = '''SELECT GROUP_CONCAT(subgenre_name, '|') FROM genres
            GROUP BY genre_id
            ORDER BY CAST(genre_id AS INTEGER), CAST(subgenre_id AS INTEGER)'''
            db.cursor.execute(sql)
            genres = [joined for joined, in db.cursor.fetchall()]
            # チャンネル情報とあわせてテンプレートに適用
            source = template.format(
                channel=channels,
                g=genres[0],
                g0=genres[1],
                g1=genres[2],
                g2=genres[3],
                g3=genres[4],
                g4=genres[5],
                g5=genres[6],
                g6=genres[7],
                g7=genres[8],
                g8=genres[9],
                g9=genres[10],
                g10=genres[11],
                g11=genres[12],
                c=channels.split('|')[0],
                d=genres[0].split('|')[0],
                d0=genres[1].split('|')[0],
                d1=genres[2].split('|')[0],
                d2=genres[3].split('|')[0],
                d3=genres[4].split('|')[0],
                d4=genres[5].split('|')[0],
                d5=genres[6].split('|')[0],
                d6=genres[7].split('|')[0],
                d7=genres[8].split('|')[0],
                d8=genres[9].split('|')[0],
                d9=genres[10].split('|')[0],
                d10=genres[11].split('|')[0],
                d11=genres[12].split('|')[0],
            )
            # 設定画面をファイルに書き出す
            with open(Common.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                f.write(source)
            # 付随するファイルを作成する
            os.makedirs(os.path.join(Common.DATA_PATH, 'settings'), exist_ok=True)
            shutil.copy(Common.SETTINGS_FILE, Common.ORIGINAL_SETTINGS)
            with open(Common.SMARTLIST_SETTINGS, 'w', encoding='utf-8') as f:
                lines = []
                for line in source.split('\n'):
                    if line.find('30100') > -1:
                        lines.append('<!--')
                    if line.find('30000') > -1:
                        lines.append('-->')
                    lines.append(line)
                f.writelines(map(lambda x: x + '\n', lines))
            # 完了
            Common.notify('Channel initialized successfully')
            return True
        else:
            Common.log('channel failed', response_body, error=True)
            Common.notify('Channel initialization failed')
            return False
    else:
        Common.log('empty response', error=True)
        Common.notify('Channel initialization failed')
        return False


def checkSettings():
    # 必須設定項目をチェック
    return Common.GET('garapon_id') and Common.GET('garapon_pw') and Common.GET('garapon_addr') and Common.GET('garapon_session')
