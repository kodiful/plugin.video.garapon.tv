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
    # データ取得
    response_body = Request().channel()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            # ファイルに書き出す
            Channel().setData(response_data)
            # チャンネル数を設定
            Common.SET('garapon_ch', '%d channels' % len(response_data['ch_list'].keys()))
            # テンプレートからsettings.xmlを生成
            data = Genre().getLabel()  # genre
            data['channel'] = Channel().getLabel()  # channel
            template = Common.read_file(Common.TEMPLATE_FILE)
            source = template.format(
                channel=data['channel'],
                genre0=data['genre0'],
                genre00=data['genre00'],
                genre01=data['genre01'],
                genre02=data['genre02'],
                genre03=data['genre03'],
                genre04=data['genre04'],
                genre05=data['genre05'],
                genre06=data['genre06'],
                genre07=data['genre07'],
                genre08=data['genre08'],
                genre09=data['genre09'],
                genre10=data['genre10'],
                genre11=data['genre11'],
            )
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
