#coding: utf-8
'''
wikipediaダンプデータから位置情報を含むものを抽出する
出力形式: title|category|lat|lng
抽出可能な表記:
    * [ウィキ座標, coord] + display=title
    * infobox内の display=inline
    * infobox内の日本語記述 | 緯度度 ... | 経度度 ...
    * infobox内の[ウィキ座標, coord]

xml.sax, cElementree.iterparse, lxmlとかを使えばXMLをメモリに全て乗せなくても解析できることが分かったので、そのうち書き換えるかも
'''
import re
import codecs
import sys

def dms_to_dd(deg=0, minute=0, sec=0):
    '''度分秒(dms)を10進角(decimal degrees)に変換'''
    return deg + minute/60 + sec/3600

def get_places_info(title, lines):
    '''display=で記述されている座標情報から抽出'''
    places=[]
    for line in lines:
        CATEGORY_re = re.search('type:(.+?)[_|}|\(|\|]', line)
        category = CATEGORY_re.group(1) if CATEGORY_re else ''
        coord = str_to_coord(line)
        if coord:
            places.append({
                          'title': title,
                          'category': category.strip(),
                          'lat': coord[0],
                          'lng': coord[1]})
    return places
        
def get_places_info_jp(title, lines):
    '''infobox内に| 緯度度 ... | 経度度 ...　
    で記述されている座標情報から抽出
    '''
    string = '\n'.join(lines)
    places=[]
    coord = str_to_coord_jp(string)
    if coord:
        places.append({
                      'title': title,
                      'category': '',
                      'lat': coord[0],
                      'lng': coord[1]})
    return places
            
def str_to_coord(string):
    '''座標情報を取得する
       dms表記はdecimal degree表記に変換する
       (南緯、西経)表記は(北緯、東経)表記に変換する
       どのような表記に対応しているかはregex_testで確認
    '''
    def strings_to_dms(strings):
        '''度分秒の文字列リストをそれぞれfloatに変換してdmsのタプルを返す
        秒が存在しない場合でも0を追加して必ずdmsを返す
        '''
        dms = map((lambda x: float(x) if x else 0.0), strings) 
        if len(dms) < 3: dms.append(0)
        return (dms[0], dms[1], dms[2])

    is_south = re.search('\|S', string)
    is_west = re.search('\|W', string)

    #dms表記
    COORD_re = re.search('\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[N,S]\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[E,W]', string)
    if COORD_re:
        lat_d, lat_m, lat_s = strings_to_dms(COORD_re.group(1).split('|'))
        lat_dd = dms_to_dd(lat_d, lat_m, lat_s)
        
        lng_d, lng_m, lng_s = strings_to_dms(COORD_re.group(4).split('|'))
        lng_dd = dms_to_dd(lng_d, lng_m, lng_s)
        
        if is_south: lat_dd *= -1
        if is_west: lng_dd *= -1

        return (lat_dd, lng_dd)
    
    #dd表記とdmsのdegree表記のみ
    COORD_re = re.search('\s?(-?\d+(\.\d+)?)\|([N,S]\|)?\s?(-?\d+(\.\d+)?)', string, re.UNICODE)
    if COORD_re:
        lat_deg = float(COORD_re.group(1))
        lng_deg = float(COORD_re.group(4))
        if is_south: lat_deg *= -1
        if is_west: lng_deg *= -1

        return (lat_deg, lng_deg)
    
    return None
    
def str_to_coord_jp(string):
    '''日本語のinfoboxでの少数派な記述方法
    | 緯度度 = 35 | 緯度分 = 38 | 緯度秒 = 3.8 | N(北緯)及びS(南緯) = N
    | 経度度 = 139 |経度分 = 47 | 経度秒 = 29.8 | E(東経)及びW(西経) = E
    に対応する
    '''
    def strings_to_dms(strings):
        '''度分秒の文字列リストをそれぞれfloatに変換してdmsのタプルを返す
        秒が存在しない場合でも0を追加して必ずdmsを返す'''
        dms = map((lambda x: float(x) if x else 0.0), strings)
        #dms[1]は度の小数点部分なので無視
        return (dms[0], dms[2], dms[3])

    is_south = re.search('=\s*?S', string, re.UNICODE)
    is_west = re.search('=\s*?W', string, re.UNICODE)
    
    try:
        lat_strings = re.search(u'緯度度\s*=\s*(-?\d+(\.\d+)?).+緯度分\s*=\s*(\d+)?.+緯度秒\s*=\s*(\d+(\.\d+)?)?', string, re.UNICODE).groups()
    except(AttributeError):
        return None
    lat_d, lat_m, lat_s = strings_to_dms(lat_strings)
    lat_dd = dms_to_dd(lat_d, lat_m, lat_s)
    
    try:
        lng_strings = re.search(u'経度度\s*=\s*(-?\d+(\.\d+)?).+経度分\s*=\s*(\d+)?.+経度秒\s*=\s*(\d+(\.\d+)?)?', string, re.UNICODE).groups()
    except(AttributeError):
        return None
    lng_d, lng_m, lng_s = strings_to_dms(lng_strings)
    lng_dd = dms_to_dd(lng_d, lng_m, lng_s)
    
    if is_south: lat_dd *= -1
    if is_west: lng_dd *= -1

    return (lat_dd, lng_dd)

if __name__ == '__main__':
    PATH = sys.argv[1]
    FILE = codecs.open(PATH, 'r', 'utf-8')
   
    #add header
    print "title|category|lat|lng"

    title = ''
    page_lines=[]
    page_lines_jp=[]
    for line in FILE:
        #末尾の空白処理
        line = line.strip()
        TITLE_re = re.search('<title>(.+)</title>', line)
        if TITLE_re:
            #座標の抽出
            places = get_places_info(title, page_lines)
            if page_lines_jp:
                places += get_places_info_jp(title, page_lines_jp)
            
            for place in places:
                string =  "%s|%s|%s|%s" % (place['title'],place['category'],place['lat'],place['lng'])
                print string.encode('utf-8')

            title = TITLE_re.group(1)
            page_lines = []
            page_lines_jp = []

        #タイトル右上に表示されている座標
        #この座標を最優先に使用する
        if re.search(u'display=.*title', line):
            page_lines.insert(0, line)
        #infobox内
        elif re.search(u'^\|.+{{[Cc]oord.+}}$', line, re.UNICODE):
            page_lines.append(line)
        elif re.search(u'^\|.+{{ウィキ座標.+}}$', line, re.UNICODE):
            page_lines.append(line)
        #緯度度、経度度は2行に分かれているので一行進める
        elif re.search(u'緯度度\s*?=\s*?\d+', line, re.UNICODE):
            page_lines_jp.append(line)
            line = FILE.next()
            page_lines_jp.append(line)
        #本文中の座標
        elif re.search(u'^\|.+display=inline', line):
            page_lines.append(line)
