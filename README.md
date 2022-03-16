# tetris_microservices
テトリスを無駄にマイクロサービスにしてみるという試みです。
現状、以下のようなアーキテクチャとなっています。

<img src="./architecture.png" width="300">

## client (html / javascript)
Webクライアント。暫定的に1秒に1回Pollingするという簡易的なもの。

## ui (javascript / node.js)
クライアントからのfieldデータ要求、Minoを動かす要求を受け付け、fieldサービス、gameサービスに振り分け

## game (go)
Gameの状態(Gameover, Game中, etc)を管理。uiからのMinoを動かす要求を、ゲーム状態に応じてMinoサービスに依頼。mainloopを持ち、Minoを定期的に落下させる処理も行う。

## mino (python)
Minoのマスタデータ管理と、インスタンス(Field上で制御対象になっているMino)管理。(ライフサイクルが違うので分離するかも)

## field (python)
Fieldデータの管理

## TODO
- clientをpollingでなくサーバpushにする。(Websocket, HTTP/2 Server Push, etc.)
- サービス間通信をOpen API化、gRPC化
- サービス間の通信を非同期にしてみる(RabbitMQ / Kafka)
- 各サービスをクラウドに載せて、クライアントとの遅延が発生する環境でも動くようにする
- docker-composeだけでなくKubernetes上にdeployできるようにする
- 各サービスをAWS Step FunctionsとLambda等で実装してみる
- 各サービスをKubernetes Operatorとして実装してみる
- Next Mino機能の実装
- Score機能の実装
- ユーザ登録機能 / High Scoreランキング機能の実装
- 2人対戦/協力モードの実装
