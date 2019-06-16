# -*- coding: utf-8 -*-

### 指定された路線を走行する列車の現在位置を表示するサンプル

import io
import sys

import odpt_api

# 標準出力の文字コードを設定
try:
    env = get_ipython().__class__.__name__
except NameError:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 取得する路線の固有識別子
railway_id = 'odpt.Railway:JR-East.Tokaido'

# 静的データ（事業者・路線・進行方向・列車種別・駅）の取得
operators = odpt_api.get_query('Operator')
railways = odpt_api.get_query('Railway')
directions = odpt_api.get_query('RailDirection')
traintypes = odpt_api.get_query('TrainType')
stations = odpt_api.get_query('Station', {'odpt:railway': railway_id})

# 列車の走行位置情報を取得して進行方向毎にまとめる
trains = odpt_api.summarize_by_key( \
           odpt_api.get_query('Train', {'odpt:railway': railway_id}), 'odpt:railDirection')

# 進行方向毎に列車の走行位置を表示
for direction_id in trains:
    # 路線・進行方向の表示
    print('\n■ %s（%s） 列車走行位置' % \
          (railways[railway_id]['dc:title'], directions[direction_id]['dc:title']))
    
    # 列車毎の処理
    for train_id in trains[direction_id]:
        train = trains[direction_id][train_id]
        
        # 列車番号 (required)
        number = train['odpt:trainNumber']
        
        # 車両数 (optional)
        if 'odpt:carComposition' in train.keys():
            cars = '%2d両' % train['odpt:carComposition']
        else:
            cars = ''
        
        # 所属会社 (optional)
        if 'odpt:trainOwner' in train.keys():
            owner = '車両: %s' % operators[train['odpt:trainOwner']]['dc:title']
        else:
            owner = ''
        
        # 列車種別 (optional)
        if 'odpt:trainType' in train.keys():
            traintype = traintypes[train['odpt:trainType']]['dc:title']
        else:
            traintype = ''
        
        # 行先 (optional)
        if 'odpt:destinationStation' in train.keys():
            destination = [odpt_api.get_station(k, stations)['dc:title'] \
                           for k in train['odpt:destinationStation']]
        else:
            destination = ''
        
        # 現在位置 (optional)
        current_station_id = []
        if 'odpt:fromStation' in train.keys() and \
        not train['odpt:fromStation'] is None:
            current_station_id.append(train['odpt:fromStation'])
            
        if 'odpt:toStation' in train and \
        not train['odpt:toStation'] is None:
            current_station_id.append(train['odpt:toStation'])
        
        current_station = [odpt_api.get_station(k, stations)['dc:title'] \
                           for k in current_station_id]

        # 遅れ時間 (optional)
        if 'odpt:delay' in train.keys():
            delay_minutes = int(train['odpt:delay'] / 60.0 + 0.5)
            delay = '平常' if delay_minutes == 0 else '%d分遅れ' % delay_minutes
        
        # 列車情報の表示
        print('[%5s] %s %s %s行き: %s （%s） %s' % \
              (number, \
               traintype, \
               cars, \
               '・'.join(destination), \
               '→'.join(current_station), \
               delay, \
               owner, \
               ))
