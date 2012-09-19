#coding: utf-8
'''
wiki_placeからmongodbに追加する
'''
import csv
from pymongo import Connection, GEO2D

if __name__ == '__main__':
    conn = Connection()
    db = conn.test
    fp = open('../wiki_place.csv', 'r')
    places = csv.DictReader(fp, delimiter='|')
    
    for place in places:
        lon = float(place['lng'])
        lat = float(place['lat'])
        if(lon < -180 or lon > 180):
#            print place['title'], place
            continue
        if(lat < -180 or lat > 180):
#            print place['title'], place
            continue
        db.wiki_place.save({'title':place['title'].decode('utf-8'),
                            'category':place['category'],
                            'coord':[lon, lat]
                            })
    
    db.wiki_place.ensure_index([('coord', GEO2D)])
    fp.close()
