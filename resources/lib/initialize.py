# -*- coding: utf-8 -*-

import json

from resources.lib.common import Common
from resources.lib.channel import Channel
from resources.lib.genre import Genre
from resources.lib.request import Request


def initializeNetwork():
    # リセット
    Common.SET('garapon_addr', '')
    Common.SET('garapon_http', '')
    Common.SET('garapon_https', '')
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
            else:
                Common.SET('garapon_http', '')
                Common.SET('garapon_https', '')
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
    # リセット
    Common.SET('garapon_ch', '')
    # チャンネル情報を取得
    response_body = Request().channel()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            # チャンネル情報をファイルに書き出す
            Common.write_json(Common.CHANNEL_FILE, response_data)
            # チャンネル数を設定
            Common.SET('garapon_ch', '%d channels' % len(response_data['ch_list'].keys()))
            # 設定画面のテンプレートを読み込む
            template = Common.read_file(Common.TEMPLATE_FILE)
            # テンプレートに書き出すジャンル情報
            genre = Genre().getLabel()
            # チャンネル情報とあわせてテンプレートに適用
            source = template.format(
                channel=Channel().getLabel(),
                g0=genre['g0'],
                g00=genre['g00'],
                g01=genre['g01'],
                g02=genre['g02'],
                g03=genre['g03'],
                g04=genre['g04'],
                g05=genre['g05'],
                g06=genre['g06'],
                g07=genre['g07'],
                g08=genre['g08'],
                g09=genre['g09'],
                g10=genre['g10'],
                g11=genre['g11']
            )
            # 設定画面をファイルに書き出す
            Common.write_file(Common.SETTINGS_FILE, source)
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
