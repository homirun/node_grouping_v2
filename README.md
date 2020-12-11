# node_grouping_v2
複数台あるノードを奇数になるようにグルーピングを行い,各グループ内に1つLeaderノードを定め,グループ内でネットワーク分断が発生した際にはLeaderノード同士が疎通の取れるグループ数で生存するかの判定を行うことにより偶数台ノードの際に障害発生しても一貫性を高めることができる手法の提案
<div align="center">
<img width="636" alt="スクリーンショット 2020-09-20 23 45 40" src="https://user-images.githubusercontent.com/9010534/101114794-8f40a380-3625-11eb-856b-37172777eafd.png">
</div>




### クラスタのステータスを確認することができるWebアプリケーション  
<img width="1529" alt="スクリーンショット 2020-11-14 16 35 41" src="https://user-images.githubusercontent.com/9010534/101114666-4e488f00-3625-11eb-9958-78d0b2bcfbfd.png">


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
