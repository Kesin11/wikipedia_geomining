#Wkipediaの記事から位置情報をマイニング
Wikipediaの記事に含まれる位置情報をマイニングしてデータベース化しやすいCSVを生成します。
このデータベースを使用したサンプルとして
[LocationTweet](http://location-tweet.herokuapp.com/)
というWebアプリを作成しました。テキストのみを使用してツイートを地図にマッピングしています。

##使用方法
http://dumps.wikimedia.org/jawiki/latest/
からjawiki-latest-pages-articles.xml.bz2をダウンロード解凍し、

```
python src/coordinate.py jawiki-latest-pages-articles.xml
```

コマンドを実行するとWikipediaのダンプXMLから抽出したデータが標準出力に表示されます。データを書き出す場合はリダイレクトを使用してください。


XMLのダウンロードからwiki_place.csv生成までの自動化スクリプトも一応用意しました。
MacOSなら動作すると思いますが、Linuxでは確かめていません。
ディレクトリのパスは末尾に'/'が入らないようにしてください
```
sh run.sh 10Gぐらい空きのあるディレクトリのパス
```

また、最新のデータでなくても構わないならwiki_place.csvを使用してください

##抽出可能な座標表現
src/regex_test.pyに正規表現のテストコードがあるのでそちらを参照してください

##抽出可能な座標表記の位置
* [ウィキ座標, coord] + display=title
* infobox内のdisplay=inline
* infobox内の日本語記述 | 緯度度 ... | 経度度 ...
* infobox内の[ウィキ座標, coord]

##出力形式

```
title|category|lat|lng
```

一部のtitleに','が含まれる記事が存在しており、csv読み込み時のズレを防ぐために区切り文字を'|'にしてあります。

##サンプル
```
title|category|lat|lng
両国国技館|landmark|35.6969166667|139.793527778
シカゴ||41.9|-87.65
スーパーカミオカンデ||36.4166666667|137.3
アメリカ航空宇宙局|landmark|38.8830555556|-77.0163888889
関西国際空港||34.4272222222|135.243888889
任天堂|landmark|34.9697222222|135.756194444
佐鳴湖||34.7105555556|137.690277778
IBM|landmark|41.1080555556|-73.72
インテル||-37.3879277778|-121.963538889
...
```

##今後の予定
error_list.txtがTODO
###対応記事の拡張
位置情報を正しく抽出できない記事への対応
###同名の重複解消
1記事内に複数の場所名が含まれる記事に対応させるため、csvを拡張する
title(記事名)|name(場所名)|category|lat|lng
###Wikipedia記事によるノイズの除去
プロジェクト, templateなどWikipediaプロジェクト由来のエントリは削除する
###リダイレクト情報の活用
例えば現状では"東京国際展示場"は抽出できるが、"ビッグサイト"では抽出できない。リダイレクト情報を活用すれば"東京国際展示場"="ビッグサイト"の対応付けが可能となるはず
