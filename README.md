# node_grouping_v2
複数台あるノードを奇数になるようにグルーピングを行い,各グループ内に1つLeaderノードを定め,グループ内でネットワーク分断が発生した際にはLeaderノード同士が疎通の取れるグループ数で生存するかの判定を行うことにより偶数台ノードの際に障害発生しても一貫性を高めることができる手法の提案

## node_grouping_v2の変更点
https://github.com/homirun/node_grouping で見つかった問題点を修正
- RESTfulなWebAPIからgRPCへ
- node_listの配布を全部ではなく差分へ

## Usage
1. ノードの起動  
```docker-compose up -d```
2. デモ用Webアプリのバックエンドの起動  
```python ./web_app/backend &```
3. デモ用Webアプリのフロントエンドの起動  
```cd web_app/frontend```
```npm run serve```
