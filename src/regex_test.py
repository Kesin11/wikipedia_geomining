#coding: utf-8
'''
正規表現のテストコード
座標の表し方には何通りかあるらしいので、統一が必要
ちゃんとwikiページと確認を取る
ある程度取れてきたら本番環境でエラーを調べて、テストに追加していく
TODO: coordだけではなく、ウィキ座標系に対応
TODO: 10進数、60進数のフォーマットに対応
TODO: dms, degree表示の変換 http://gis.stackexchange.com/questions/16555/converting-from-dms-to-dd-using-python-in-field-calculator , http://www.rottel.net/kuwa/12403
http://stackoverflow.com/questions/6460381/translate-exif-dms-to-dd-geolocation-with-python
TODO: 基本はNEだけどSWでの符号反転への対応もしないとマズイ
'''
import unittest
import coordinate

class RegexTest(unittest.TestCase):
    def setUp(self):
        pass
    def test_deg1(self):
        #小数点
        #総務省 landmark
        string = "{{Coord|35.675366|139.7511182|type:landmark_region:JP|display=inline,title|name=MIC}}"
        ans = (35.675366, 139.7511182)
        self.assertEqual(ans, coordinate.get_coord(string))
    def test_deg2(self):
        #小数点マイナス（西系表示）
        #真珠湾
        string = "{{Coord|21.359255|-157.951813|format=dms|display=title}}"
        ans = (21.359255, -157.951813)
        self.assertEqual(ans, coordinate.get_coord(string))
    def test_deg3(self):
        #小数点 スペースを含む
        #築地
        string = "{{Coord|35.66819| 139.77390|format=dms|display=title}}"
        ans = (35.66819, 139.7739)
        self.assertEqual(ans, coordinate.get_coord(string))
    def test_deg4(self):
        #小数点 NE区切り
        #ノートルダム大聖堂 (パリ) landmark
        string = "{{Coord|48.8530|N|2.3498|E|type:landmark_region:FR|display=title}}"
        ans = (48.8530, 2.3498)
        self.assertEqual(ans, coordinate.get_coord(string))
    def test_dms1(self):
        #1桁区切り
        #黒海 waterbody
        string = "{{Coord|44|N|35|E|type:waterbody_scale:8000000 |display=title}}"
        ans = (44, 35)
        self.assertEqual(ans, coordinate.get_coord(string))
    #------以下はdms -> degreeの変換が必要-----
    #テストコードで小数点の有効桁数を合わせるために一工夫
    def test_dms2(self):
        #2桁区切り
        #デルポイ landmark
        string = "{{Coord|38|29|N|22|30|E|type:landmark_region:GR|display=title}}"
        ans = (38.483333, 22.5)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms3(self):
        #3桁区切り
        #欧州中央銀行
        string = "|coordinates = {{Coord|50|6|34|N|8|40|26|E|display=inline,title}}"
        ans = (50.109444, 8.673889)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms4(self):
        #3桁区切り3桁目小数点
        #203高地 
        string = "{{Coord|38|49|43.10|N|121|11|36.30|E|display=title}}"
        ans = (38.828639, 121.193417)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms5(self):
        #3桁区切り 3桁目空白
        #蒲郡市 city
        string = "{{Coord|34|50||N|137|13||E|region:JP_type:city|display=title}}"
        ans = (34.833333, 137.216667)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms6(self):
        #3桁区切り 南緯表示
        #サボ島
        string = "{{Coord|09|08|00|S|159|49|00|E|display=title}}"
        ans = (-9.133333, 159.816667)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms7(self):
        #3桁区切り 西経表示
        #サンフランシスコ国際空港 airport 
        string = "| coordinates  = {{Coord|37|37|08|N|122|22|30|W|region:US-CA_type:airport|display=inline,title}}"
        ans = (37.618889, -122.375)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    def test_dms8(self):
        #3桁区切り 南緯西経表示
        #南極点
        string = '<text xml:space="preserve">{{Coord|90|S|0|W|display=title}}'
        ans = (-90, 0)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord(string))
        self.assertEqual(ans, tuple(latlng))
    #------以下はinfobox内での少数派の記述方法------
    def test_jp1(self):
    #東京国際展示場
        string = u"""| 緯度度 = 35 | 緯度分 = 37 | 緯度秒 = 48.57 | N(北緯)及びS(南緯) = N 
| 経度度 = 139 |経度分 = 47 | 経度秒 = 37.47 | E(東経)及びW(西経) = E"""
        ans = (35.630158, 139.793742)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord_jp(string))
        self.assertEqual(ans, tuple(latlng))
    def test_jp2(self):
    #スペース無し
    #広畑駅
        string = u"""|緯度度=34|緯度分=47|緯度秒=51.92
|経度度=134|経度分=37|経度秒=41.31"""
        ans = (34.797756, 134.628142)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord_jp(string))
        self.assertEqual(ans, tuple(latlng))
    def test_jp3(self):
    #緯度秒が空白
    #シカゴ
        string = u"""|緯度度 = 41 |緯度分 = 54 |緯度秒 = |N(北緯)及びS(南緯) = N
|経度度 = 87 |経度分 = 39 |経度秒 = |E(東経)及びW(西経) = W"""
        ans = (41.9, -87.65)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord_jp(string))
        self.assertEqual(ans, tuple(latlng))
    def test_jp4(self):
    #緯度度に全て記入
    #シカゴ
        string = u"""|緯度度 = 51.922832 |緯度分 = |緯度秒 = |N(北緯)及びS(南緯) = N
|経度度 = 4.479606 |経度分 = |経度秒 = |E(東経)及びW(西経) = E"""
        ans = (51.922832, 4.479606)
        latlng = map(lambda x: round(x, 6), coordinate.get_coord_jp(string))
        self.assertEqual(ans, tuple(latlng))

if __name__ == '__main__':
    unittest.main()