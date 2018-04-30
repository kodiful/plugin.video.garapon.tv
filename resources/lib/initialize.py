# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time
import codecs
import json

from const import Const
from channel import Channel
from genre import Genre
from request import Request

#-------------------------------------------------------------------------------
def initializeNetwork():
    # リセット
    Const.SET('garapon_addr', '')
    Const.SET('garapon_http', '')
    Const.SET('garapon_https', '')
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
            except:
                pass
        if params['message'] == 'success':
            Const.SET('garapon_addr', params['ipaddr'])
            if params['ipaddr'] == params['gipaddr']:
                Const.SET('garapon_http', params['port'])
                Const.SET('garapon_https', params['port2'])
            else:
                Const.SET('garapon_http', '')
                Const.SET('garapon_https', '')
            return True
        else:
            log('getgtvaddress failed', error=True)
            notify('Network initialization failed')
            return False
    else:
        log('empty response', error=True)
        notify('Network initialization failed')
        return False

#-------------------------------------------------------------------------------
def initializeSession():
    # リセット
    Const.SET('garapon_session', '')
    # データ取得
    response_body = Request().auth()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            if response_data['login'] == 1:
                gtvsession = response_data['gtvsession']
                Const.SET('garapon_session', gtvsession)
                Const.SET('garapon_authtime', str(time.time()))
                return True
            else:
                log('auth failed', error=True)
                notify('Session initialization failed')
                return False
        else:
            log('auth failed', error=True)
            notify('Session initialization failed')
            return False
    else:
        log('empty response', error=True)
        notify('Session initialization failed')
        return False

#-------------------------------------------------------------------------------
def initializeChannel():
    # リセット
    Const.SET('garapon_ch', '')
    # データ取得
    response_body = Request().channel()
    if response_body:
        response_data = json.loads(response_body)
        if response_data['status'] == 1:
            # ファイルに書き出す
            Channel().setData(response_data)
            # チャンネル数を設定
            Const.SET('garapon_ch', '%d channels' % len(response_data['ch_list'].keys()))
            # テンプレートからsettings.xmlを生成
            data = Genre().getLabel() # genre
            data['channel'] = Channel().getLabel() # channel
            f = codecs.open(Const.TEMPLATE_FILE,'r','utf-8')
            template = f.read()
            f.close()
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
                genre11=data['genre11'])
            f = codecs.open(Const.SETTINGS_FILE,'w','utf-8')
            f.write(source)
            f.close()
            # 完了
            return True
        else:
            log('channel failed', error=True)
            notify('Channel initialization failed')
            return False
    else:
        log('empty response', error=True)
        notify('Channel initialization failed')
        return False

#-------------------------------------------------------------------------------
def checkSettings():
    # 必須設定項目をチェック
    if Const.GET('garapon_id') and Const.GET('garapon_pw') and Const.GET('garapon_addr') and Const.GET('garapon_session'):
        return True
    else:
        return False

#-------------------------------------------------------------------------------
def syncSession(url):
    # パラメータ抽出
    o = urlparse.urlparse(url)
    args = urlparse.parse_qs(o.query)
    for key in args.keys(): args[key] = args[key][0]
    # サーバの設定値
    url = urlparse.urlunparse((o[0],o[1],o[2],'','',''))
    credential = args.get('credential','')
    server_session = args.get('gtvsession','')
    server_authtime = args.get('authtime','')
    # クライアントの設定値
    client_session = Const.GET('garapon_session')
    client_authtime = Const.GET('garapon_authtime')
    # 最新のgtvsessionを判定
    if float(server_authtime) > float(client_authtime):
        # サーバの設定をクライアントに反映
        Const.SET('garapon_session', server_session)
        Const.SET('garapon_authtime', server_authtime)
        gtvsession = server_session
        authtime = server_authtime
        authupdate = False
    else:
        # クライアントの設定をサーバに反映
        gtvsession = client_session
        authtime = client_authtime
        authupdate = True
    # サーバへ通知
    response_body = Request().sync(url, credential, gtvsession, authtime, authupdate)
    if response_body:
        response_data = json.loads(response_body)
        if response_data['result'] == 'OK':
            return True
        else:
            log('sync failed', error=True)
            notify('Sync session failed')
            return False
    else:
        log('empty response', error=True)
        notify('Sync session failed')
        return False
