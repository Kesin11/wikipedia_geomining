#coding: utf-8
'''
wikipediaダンプデータから位置情報を含むものを抽出する
ただし事件などのthingsは抽出しない
* infoウィンドウから座標抽出
* [ウィキ座標, coord] + display=titleはOK。それ以外は後で考える
* typeを抽出。eventは除いておく
* landmark_regionのように載っていないタイプもある
* display, titleは順番通りに並んでいるとは限らない
* infoboxにしか座標がないこともある
  * | coordinates
  * [ウィキ座標, coord]が存在する行を抜き出して一時保存してから解析するか？
'''
import re
import codecs

if __name__ == '__main__':
    PATH = "/Users/kase/Downloads/wikidump_2012_03/jawiki-latest-pages-articles.xml"
    file = codecs.open(PATH, 'r', 'utf-8')
    