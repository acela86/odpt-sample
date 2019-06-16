# -*- coding: utf-8 -*-

### 各鉄道事業者の路線と駅を表示するサンプル

import io
import sys

import odpt_api

# 標準出力の文字コードを設定
try:
    env = get_ipython().__class__.__name__
except NameError:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 必要なデータを取得（事業者・進行方向・路線）
operators = odpt_api.get_query('Operator')
directions = odpt_api.get_query('RailDirection')
railways = odpt_api.get_query('Railway')

# 路線情報を事業者ごとにまとめる
operator_railways = odpt_api.summarize_by_key(railways, 'odpt:operator')

# 事業者毎に路線と駅を表示する
for operator_key in operator_railways.keys():
    # 事業者名と固有識別子の表示
    print('\n■ %s (%s)' % \
          (operators[operator_key]['dc:title'], operator_key))

    # 路線毎の処理
    for railway_key in operator_railways[operator_key].keys():
        railway = operator_railways[operator_key][railway_key]
        
        # 路線名の表示
        print('\n□ %s (%s)' % \
              (railway['dc:title'], railway_key))
        
        # 進行方向の表示
        if 'odpt:descendingRailDirection' in railway.keys():
            print('↑%s(%s)\n↓%s(%s)' % \
                  (directions[railway['odpt:descendingRailDirection']]['dc:title'],
                   directions[railway['odpt:descendingRailDirection']]['owl:sameAs'],
                   directions[railway['odpt:ascendingRailDirection']]['dc:title'],
                   directions[railway['odpt:ascendingRailDirection']]['owl:sameAs']))
        
        # 各駅の順序・駅名・固有識別子の表示
        for station in railway['odpt:stationOrder']:
            print("[%02d] %s (%s)" % \
                  (station['odpt:index'],
                   station['odpt:stationTitle']['ja'],
                   station['odpt:station']))
