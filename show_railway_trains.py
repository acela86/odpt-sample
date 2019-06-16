# -*- coding: utf-8 -*-

# 指定された日付・路線の列車一覧を表示するサンプル

import io
import sys
import datetime

import odpt_api
import jp_holiday

# 標準出力の文字コードを設定
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 取得する路線の固有識別子
railway = 'odpt.Railway:JR-East.Tokaido'

# 必要なデータを取得（路線・進行方向・列車種別・カレンダー・駅・時刻表）
railways = odpt_api.get_query('Railway')
directions = odpt_api.get_query('RailDirection')
traintypes = odpt_api.get_query('TrainType')
calendars = odpt_api.get_query('Calendar')
stations = odpt_api.get_query('Station', {'odpt:railway': railway})
timetables = odpt_api.get_query('TrainTimetable', {'odpt:railway': railway})
direction_timetables = odpt_api.summarize_by_key(timetables, 'odpt:railDirection')

# 日付区分を取得
holidays = jp_holiday.get_holidays()
day = odpt_api.get_days(datetime.datetime.now(), holidays, calendars)

# 進行方向毎に列車を表示
for d in direction_timetables.keys():
    # 進行方向の表示
    print('\n■ %s' % directions[d]['dc:title'])
    
    # 列車毎の処理
    for v in direction_timetables[d].values():
        # 日付区分が一致しない場合はスキップ
        if 'odpt:calendar' in v.keys() and \
        not v['odpt:calendar'] in day:
            continue

        # 列車種別 (optional)
        if 'odpt:trainType' in v.keys():
            traintype = traintypes[v['odpt:trainType']]['dc:title']
        else:
            traintype = ''
            
        # 列車名 (optional)
        trainname = v['odpt:trainName'] if 'odpt:trainName' in v.keys() else ''
            
        # 始発駅
        if 'odpt:originStation' in v.keys():
            origin = \
                [odpt_api.get_station(k, stations)['dc:title'] \
                 for k in v['odpt:originStation']]
        else:
            origin = []
        
        # 終着駅
        if 'odpt:destinationStation' in v.keys():
            destination = \
                [odpt_api.get_station(k, stations)['dc:title'] \
                 for k in v['odpt:destinationStation']]
        else:
            destination = []
            
        # 直前の列車時刻表
        prev_timetables = []
        if 'odpt:previousTrainTimetable' in v.keys():
            for t in v['odpt:previousTrainTimetable']:
                s = t.split(':')[1].split('.')
                
                # 路線が異なる場合は路線名を列車番号の前に付加
                prev_railway_key = 'odpt.Railway:%s.%s' % (s[0], s[1])
                if prev_railway_key != railway and prev_railway_key in railways:
                    prev_railway = railways[prev_railway_key]['dc:title']
                else:
                    prev_railway = ''
                
                prev_timetables.append('%s%s' % (prev_railway, s[2]))
                
        # 直後の列車時刻表
        next_timetables = []
        if 'odpt:nextTrainTimetable' in v.keys():
            for t in v['odpt:nextTrainTimetable']:
                s = t.split(':')[1].split('.')
                
                # 路線が異なる場合は路線名を列車番号の前に付加
                next_railway_key = 'odpt.Railway:%s.%s' % (s[0], s[1])
                if next_railway_key != railway and next_railway_key in railways:
                    next_railway = railways[next_railway_key]['dc:title']
                else:
                    next_railway = ''
                
                next_timetables.append('%s%s' % (next_railway, s[2]))        
    
        # 列車番号・行先・直前直後の時刻表の表示
        label = ''
        if len(prev_timetables) > 0:
            label += '（%s） ' % '・'.join(prev_timetables)
    
        label += '・'.join(origin) + '→'
        label += '・'.join(destination)
        
        if len(next_timetables) > 0:
            label += ' （%s）' % '・'.join(next_timetables)
        
        train_number = v['odpt:trainNumber']
        
        print('[%s] %s %s %s' % (train_number, trainname, traintype, label))