#coding: utf-8
'''
wiki_place.csvからmongodbして地理インデックスを貼る
'''
import csv
from pymongo import Connection, GEO2D

def in_earth(lat, lon):
    if(lon <= -180.0 or lon >= 180.0):
        return False
    if(lat <= -180.0 or lat >= 180.0):
        return False
    return True

def in_japan(lat, lon):
    '''日本国内の座標であるか判定
    最東端：南鳥島
    最西端：与那国島西崎
    最南端：沖ノ鳥島
    最北端：弁天島
    '''
    if(lon <= 122.93361 or lon >= 153.980555556):
        return False
    if(lat <= 20.425556 or lat >= 45.526389):
        return False
    return True

if __name__ == '__main__':
    conn = Connection()
    db = conn.wikipedia
    fp = open('wiki_place.csv', 'r')
    places = csv.DictReader(fp, delimiter='|')
    
    for place in places:
        lat = float(place['lat'])
        lon = float(place['lng'])
        #If you want save place only in japan, comment out 'in_japan()'
        if in_earth(lat, lon):
        #if in_japan(lat, lon):
            db.places.save({'title':place['title'].decode('utf-8'),
                            'category':place['category'],
                            'coord':[lon, lat]
                            })
    
    db.places.ensure_index([('coord', GEO2D)])
    fp.close()
