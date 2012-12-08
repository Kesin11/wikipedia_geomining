#!/bin/bash

#WikipediaのダンプデーターのダウンロードからCSVの抽出までの自動化スクリプト
#注意！ Wikipediaの巨大なXMLのダウンロード、解凍を行いますので十分に余裕のあるディレクトリを引数に与えて実行してください

#引数のファイルパスにWikipediaのダンプデーターをダウンロード
DOWNLOAD_FILE=${1}/jawiki-latest-pages-articles.xml.bz2
XML_FILE=${1}/jawiki-latest-pages-articles.xml

echo "Downloading latest wikipedia articles dump..."
curl -# -o $DOWNLOAD_FILE http://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2
echo "Decompress bz2..."
bzip2 -dc $DOWNLOAD_FILE > $XML_FILE

echo "Parsing XML file..."
mv wiki_place.csv wiki_place.csv.old
python src/coordinate.py $XML_FILE > wiki_place.csv

#昔のwiki_place.csvとの差分出力
echo "Make wiki_place.csv and wiki_place.csv.old diff file"
diff wiki_place.csv wiki_place.csv.old > diff_latest

echo "Entry number:"
wc -l wiki_place.csv
wc -l wiki_place.csv.old

echo "Done!"
