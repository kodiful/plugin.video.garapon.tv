# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import xbmc
import xbmcgui

from resources.lib.common import Common
from resources.lib.db import DB, ThreadLocal


class Service(Common):

    # 番組情報更新確認のインターバル（秒）
    MAX_INTERVAL = 60
    MIN_INTERVAL = 10
    LAG_REFRESH = -30

    def __init__(self):
        # DBの共有インスタンス
        db = ThreadLocal.db
        # 既存の番組情報を削除
        db.cursor.execute('DELETE FROM contents')

    def monitor(self):
        # 開始
        self.log('enter monitor.')
        # 監視開始を通知
        self.notify('Starting service', duration=3000)
        # スレッドのDBインスタンスを作成
        ThreadLocal.db = db = DB()
        # 監視を開始
        monitor = xbmc.Monitor()
        while monitor.abortRequested() is False:
            # デフォルトインターバル
            check_interval = self.MAX_INTERVAL
            # 表示中の画面を確認
            win = xbmcgui.getCurrentWindowId()  # 100025
            dlg = xbmcgui.getCurrentWindowDialogId()  # 9999 -> 10140
            path = xbmc.getInfoLabel('Container.FolderPath')  # plugin://plugin.video.garapon.tv/
            argv = 'plugin://%s/' % Common.ADDON_ID
            if path.startswith(argv) and path.find('searchOnAir') > -1:
                # 番組情報を検索
                dt = [self.MAX_INTERVAL]
                db.cursor.execute('SELECT MAX(startdate), duration FROM contents GROUP BY bc')
                for startdate, duration in db.cursor.fetchall():
                    # 2025-04-16 10:25:00|03:30:00
                    h, m, s = map(int, duration.split(':'))
                    enddate = self.datetime(startdate) + timedelta(hours=h, minutes=m, seconds=s)
                    remaining = enddate - datetime.now()
                    dt.append(remaining.total_seconds())
                if min(dt) < self.LAG_REFRESH:
                    xbmc.executebuiltin('Container.Refresh')
                check_interval = max(min(dt), self.MIN_INTERVAL)
            monitor.waitForAbort(check_interval)
        self.httpd.shutdown()
        # スレッドのDBインスタンスを終了
        db.conn.close()
        # 監視終了を通知
        self.log('exit monitor.')
