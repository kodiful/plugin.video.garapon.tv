# Kodiアドオン：ガラポンTVクライアント

ガラポンTVを操作するためのKodiアドオンです。


## 目次

[初回起動時の設定](#初回起動時の設定)

[ホーム画面と検索](#ホーム画面と検索)

[番組のサブメニュー操作](#番組のサブメニュー操作)

[スマートリストの編集](#スマートリストの編集)

[アドオン設定画面-ガラポンTV設定](#アドオン設定画面-ガラポンTV設定)

[アドオン設定画面-その他の設定](#アドオン設定画面-その他の設定)

[アドオン設定画面-スマートリスト](#アドオン設定画面-スマートリスト)


## 初回起動時の設定

初回起動時にはアドオン設定画面が表示されます。

![アドオン設定画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/dc3182eb-e946-482a-b625-5c3033898c4e)


ガラポンIDおよびパスワードを入力して「設定を更新」を選択してください（「OK」を選択しても設定は更新されません）。

あとは自動的に、入力したガラポンIDとパスワードでガラポンWeb認証を行い、ガラポンTV端末のIPアドレスを取得、さらに、取得したIPアドレスに対して、ガラポンTV端末が対応する放送局情報をリクエストし、アドオンの情報を更新します。

以上で初期設定は完了です。


## ホーム画面と検索

初回起動時の設定が完了すると、ホーム画面が表示されます。

![ホーム画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/752a9ede-5674-4133-99a7-5850f77aa16e)

### 放送中の番組

現在放送中の番組のリストが表示されます。

![放送中の番組](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/cb2e65ed-d39d-4369-a8ba-47cfd8c55c02)

ここで見たい番組を選択すると、番組が再生されます（Kodiの設定によっては詳細情報が表示されます）。

### 検索：日付

ガラポンTV端末に録画されている番組を検索します。
日付→チャンネル→ジャンルの順に検索条件を設定します。まず、日付を選択します。

![日付選択画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/4d465db9-f3ca-403c-8584-aeae11a1e71c)

次にチャンネルを選択します。

![チャンネル選択画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/9ba8b16d-d42d-4064-a7a6-086df8df439e)

次にジャンルを選択します。

![ジャンル選択画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/aff4d306-2a76-445c-9d40-214b2a8d0fca)

次にサブジャンルを選択します。選択後、検索が実行されます。

![サブジャンル選択画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/10b71645-74fd-4b47-8ac5-e58b947ed1f4)

検索結果が表示されます。

![検索結果画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/9020f95e-5335-473c-a860-b62489677046)

ここで見たい番組を選択すると、番組が再生されます（Kodiの設定によっては詳細情報が表示されます）。

### 検索：チャンネル

検索条件を、チャンネル→ジャンル→日付の順に設定するほかは「検索：日付」と同様です。

### 検索：ジャンル

検索条件を、ジャンル→チャンネル→日付の順に設定するほかは「検索：日付」と同様です。

### お気に入り

ガラポンTV端末に「お気に入り」として録画されている番組を表示します。


## 番組のサブメニュー操作

番組を選択した状態でサブメニューを表示し、その番組に関する操作を行うことができます。

![サブメニュー](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/ffc0879d-e5d2-4c12-913f-ff116226836a)

### 詳細情報

選択されている番組の詳細情報を表示します。

![サブメニュー](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/0caae1c0-c1fc-4c57-ad56-cbe664e430b7)

### スマートリストに追加

選択されている番組の番組情報に基づいて、スマートリストの編集画面を表示します。
スマートリストとは、帯番組の検索などをワンクリックで実行するために、チャンネル、ジャンル、キーワードなどの検索条件をまとめて保存するものです。

![スマートリストに追加](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/30e20346-ebeb-4c14-b1f7-77f9d5cf32d8)

キーワード等を編集します。

![スマートリストに追加](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/df885309-01d0-4148-8665-6cbc65d7a22b)

「スマートリストを追加」を選択して追加操作は完了です。スマートリストがホーム画面に追加されます。

![スマートリストに追加](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/b31d071e-8eb2-40d1-9301-aee804b7f474)

追加されたスマートリストを選択すると、設定したチャンネル、ジャンル、キーワードなどにマッチする番組が検索結果として表示されます。

![スマートリストに追加](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/04a8d220-b014-4e84-a452-c63b25e88a82)

### お気に入りに追加

選択されている番組をガラポンTV端末の「お気に入り」に追加します。

### お気に入りから削除

選択中の番組が、すでに「お気に入り」に追加されている場合は、「お気に入りに追加」の代わりに「お気に入りから削除」がサブメニューに表示されます。
これを選択すると、選択されている番組がガラポンTV端末の「お気に入り」から削除されます。


## スマートリストの編集

スマートリストを選択した状態でサブメニューを表示し、そのスマートリストの編集、削除を行うことができます。

![アドオン設定画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/ae581bb1-b63c-4018-9536-0a665057ff3f)

### スマートリストを編集

スマートリスト編集画面が表示されます。

![スマートリスト編集画面](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/5b9aff8c-7587-409d-994e-82d7e546a7fa)

編集した後、「スマートリストを変更」を選択してください。

### スマートリストを削除

選択されたスマートリストが削除されます。


## アドオン設定画面-ガラポンTV設定

![アドオン設定画面（ガラポンTV設定）](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/6d8647b0-68c6-4269-9081-0679bdb6795b)

### ガラポンID

ガラポンTV端末にアクセスするためのIDです。

### パスワード

ガラポンTV端末にアクセスするためのパスワードです。

### IPアドレス・ポート自動設定

通常はこれをチェックしてください。IPアドレス等は、ガラポンWeb認証によって自動的に取得されます。

### IPアドレス

ガラポンTV端末のIPアドレスです。

### HTTPポート

ガラポンTV端末のHTTPポートです。

### HTTPSポート

ガラポンTV端末のHTTPSポートです。

### 設定を更新

設定を変更した場合に選択してください。


## アドオン設定画面-その他の設定

![アドオン設定画面（その他の設定）](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/9706c15e-06ff-42d7-aeb8-440a3e86406d)

### サムネイルキャッシュをクリア

アドオンが生成した番組のサムネイルの容量が表示されます。必要に応じてクリアしてください。

### セッションIDを更新

セッションIDは自動的に管理されますので、通常この機能を使用することはありません。

### チャンネルリストを更新

チャンネルリストは自動的に管理されますので、通常この機能を使用することはありません。

### デバッグ

デバッグ用の設定です。 動作に関する情報をKodiのログファイルに書き出します。


## アドオン設定画面-スマートリスト

![アドオン設定画面（スマートリスト）](https://github.com/kodiful/plugin.video.garapon.tv/assets/12268536/1ad243c2-9c64-4191-8056-8d9633c036c5)

スマートリストの編集画面です。スマートリストとは、帯番組の検索などをワンクリックで実行するために、チャンネル、ジャンル、キーワードなどの検索条件をまとめて保存するものです。

チャンネル、ジャンル、検索対象、キーワードを設定して「スマートリストを追加する」を選択してください。
テレビリモコンで操作する場合は日本語入力ができないので、[番組のサブメニュー操作](#番組のサブメニュー操作)に記載した、番組情報に基づいてスマートリストを編集する方法がおすすめです。


