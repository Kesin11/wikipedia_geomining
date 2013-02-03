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
        
def get_places_info_jp(title, string):
    '''infobox内に| 緯度度 ... | 経度度 ...　
        で記述されている座標情報から抽出'''
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
       dms表記はdegree表記に変換する
       (南緯、西経)表記は(北緯、東経)表記に変換する
       どのような表記に対応しているかはregex_testで確認
    '''
    is_south = re.search('\|S', string)
    is_west = re.search('\|W', string)
    #dms表記
    COORD_re = re.search('\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[N,S]\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[E,W]', string)
    if COORD_re:
        lat_dms = map((lambda x: float(x) if not x == '' else 0), COORD_re.group(1).split('|'))
        if len(lat_dms) < 3: lat_dms.append(0)
        lat_deg = lat_dms[0] + lat_dms[1]/60 + lat_dms[2]/3600
        
        lng_dms = map((lambda x: float(x) if not x == '' else 0), COORD_re.group(4).split('|'))
        if len(lng_dms) < 3: lng_dms.append(0)
        lng_deg = lng_dms[0] + lng_dms[1]/60 + lng_dms[2]/3600
        
        if is_south: lat_deg *= -1
        if is_west: lng_deg *= -1

        return (lat_deg, lng_deg)
    
    #deg表記とdmsの度表記のみ
    COORD_re = re.search('\s?(-?\d+(\.\d+)?)\|([N,S]\|)?\s?(-?\d+(\.\d+)?)', string, re.UNICODE)
    if COORD_re:
        lat_deg = float(COORD_re.group(1))
        lng_deg = float(COORD_re.group(4))
        if is_south: lat_deg *= -1
        if is_west: lng_deg *= -1

        return (lat_deg, lng_deg)
    
    return None
    
def str_to_coord_jp(string):
    """日本語のinfoboxでの少数派な記述方法
    | 緯度度 = 35 | 緯度分 = 38 | 緯度秒 = 3.8 | N(北緯)及びS(南緯) = N
    | 経度度 = 139 |経度分 = 47 | 経度秒 = 29.8 | E(東経)及びW(西経) = E
    に対応する"""
    is_south = re.search('=\s*?S', string, re.UNICODE)
    is_west = re.search('=\s*?W', string, re.UNICODE)
    
    try:
        lat_dms = re.search(u'緯度度\s*=\s*(-?\d+(\.\d+)?).+緯度分\s*=\s*(\d+)?.+緯度秒\s*=\s*(\d+(\.\d+)?)?', string, re.UNICODE).groups()
    except(AttributeError):
        return None
    lat_dms = map((lambda x: float(x) if x else 0), lat_dms)
    #緯度度に全て記述されてるときはdmf -> deg 変換を行わない
    if not lat_dms[1] == 0:
        lat_deg = lat_dms[0]
    else:
        lat_deg = lat_dms[0] + lat_dms[2]/60 + lat_dms[3]/3600
    
    try:
        lng_dms = re.search(u'経度度\s*=\s*(-?\d+(\.\d+)?).+経度分\s*=\s*(\d+)?.+経度秒\s*=\s*(\d+(\.\d+)?)?', string, re.UNICODE).groups()
    except(AttributeError):
        return None
    lng_dms = map((lambda x: float(x) if x else 0), lng_dms)
    if not lng_dms[1] == 0:
        lng_deg = lng_dms[0]
    else:
        lng_deg = lng_dms[0] + lng_dms[2]/60 + lng_dms[3]/3600
    
    if is_south: lat_deg *= -1
    if is_west: lng_deg *= -1

    return (lat_deg, lng_deg)

if __name__ == '__main__':
    PATH = sys.argv[1]
    FILE = codecs.open(PATH, 'r', 'utf-8')
   
    #add header
    print "title|category|lat|lng"

    title = ''
    page_lines=[]
    page_lines_jp=[]
    line =  FILE.readline()
    while line:
        #末尾の空白処理
        line = line.strip()
        TITLE_re = re.search('<title>(.+)</title>', line)
        if TITLE_re:
            #座標の抽出
            places=[]
            places = get_places_info(title, page_lines)
            if page_lines_jp:
                places += get_places_info_jp(title, '\n'.join(page_lines_jp))
            
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
            line = FILE.readline()
            page_lines_jp.append(line)
        #本文中の座標
        elif re.search(u'^\|.+display=inline', line):
            page_lines.append(line)
        line = FILE.readline()
