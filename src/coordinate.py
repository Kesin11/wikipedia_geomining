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
import sys

def get_place_info(lines):
    try:
        title = re.search('<title>(.+)</title>', lines.pop(0)).group(1)
    except(AttributeError):
        print "error" , lines
    for line in lines:
        #ex. display=inline,title
        if re.search('display=.*title', line):
            #ex. type:edu_region  type:waterbody|display
            type_re = re.search('type:(.+?)[_|}|\|]', line)
            type = type_re.group(1) if type_re else ''
            print title, type,
            coord = get_coord(line)
            print coord
            print line.strip()
            print "-------------------------------------------"
            
def get_coord(string):
    '''座標情報を取得する
       dms表記はdegree表記に変換する
       (南緯、西経)表記は(北緯、東経)表記に変換する
       どのような表記に対応しているかはregex_testで確認
    '''
    is_south = re.search('\|S', string)
    is_west = re.search('\|W', string)
    coord_re = re.search('\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[N,S]\|(\d+\|\d+(\|?\d*?)?(\.\d+)?)\|[E,W]', string)
    if coord_re:
        lat_dms = map((lambda x: float(x) if not x == '' else 0), coord_re.group(1).split('|'))
        if len(lat_dms) < 3: lat_dms.append(0)
        lat_deg = lat_dms[0] + lat_dms[1]/60 + lat_dms[2]/3600
        
        lng_dms = map((lambda x: float(x) if not x == '' else 0), coord_re.group(4).split('|'))
        if len(lng_dms) < 3: lng_dms.append(0)
        lng_deg = lng_dms[0] + lng_dms[1]/60 + lng_dms[2]/3600
        
        if is_south: lat_deg *= -1
        if is_west: lng_deg *= -1
        return (lat_deg, lng_deg)
    
    coord_re = re.search('(-?\d+(\.\d+)?)\|([N,S]\|)?(-?\d+(\.\d+)?)', string)
    if coord_re:
        lat_deg = float(coord_re.group(1))
        lng_deg = float(coord_re.group(4))
        if is_south: lat_deg *= -1
        if is_west: lng_deg *= -1
        return (lat_deg, lng_deg)
    
    assert coord_re, "No match: " + string
    

if __name__ == '__main__':
    PATH = "/Users/Kenta/Downloads/wikidump_2012_03/jawiki-latest-pages-articles.xml"
    file = codecs.open(PATH, 'r', 'utf-8')
    page_lines=['<title>dammy</title>']
    count = 0
    line =  file.readline()
    while line:
        if count > 10:
            sys.exit()
        if re.search('<title>(.+)</title>', line):
            get_place_info(page_lines)
            page_lines=[]
            page_lines.append(line)
        if re.search('{{Coord.+}}', line):
            page_lines.append(line)
        line = file.readline()
        