# -*- coding: utf-8 -*-

### 東京公共交通オープンデータチャレンジ データ取得ライブラリ
### ※使用する前にアクセストークンを環境変数ODPT_KEYに格納すること

import requests
import json
import os
from datetime import datetime

import jp_holiday

# URL・アクセストークン
api_key = os.environ['ODPT_KEY']
api_url = ("https://api-tokyochallenge.odpt.org/api/v4/odpt:{RDF_TYPE}?acl:consumerKey=%s&{QUERY}" % api_key)
dump_url = ("https://api-tokyochallenge.odpt.org/api/v4/odpt:{RDF_TYPE}.json?acl:consumerKey=%s" % api_key)

# 曜日
week = ['odpt.Calendar:Monday', \
        'odpt.Calendar:Tuesday', \
        'odpt.Calendar:Wednesday', \
        'odpt.Calendar:Thursday', \
        'odpt.Calendar:Friday', \
        'odpt.Calendar:Saturday', \
        'odpt.Calendar:Sunday', \
        ]

def get_data(url, **kwargs):
    """指定されたURLからデータを取得する
    取得したデータは'owl:sameAs'フィールドの値をキーとした辞書型に変換される。
    キーは一意であることが前提。同じキーが複数存在する場合はいずれか一つのみ格納される。
    ステータスコードが200（正常終了）以外の場合はrequestで定義された例外が発生する。
    
    Args:
        url: URL
        **kwargs: requestに渡す引数
        
    Returns：
        dict: 取得したJSONデータ（辞書型）
    
    """
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return convert_to_dict(json.loads(response.text))

def get_query(rdf_type, query={}, **kwargs):
    """データ検索APIを用いてデータを取得する
    動作の詳細はget_dataの説明を参照。
    
    Args:
        rdf_type: データ種別（'odpt:'は不要）
        query: クエリ（辞書型）
        **kwargs: requestに渡す引数
    
    Returns:
        dict: 取得したJSONデータ（辞書型）
        
    """
    
    param = '&'.join([key + '=' + query[key] for key in query])
    url = api_url.format(RDF_TYPE=rdf_type, QUERY=param)
    return get_data(url, **kwargs)

def get_dump(rdf_type, **kwargs):
    """データダンプAPIを用いてデータを取得する
    動作の詳細はget_dataの説明を参照。
    
    Args:
        rdf_type: データ種別（'odpt:'は不要）
        **kwargs: requestに渡す引数
    
    Returns:
        dict: 取得したJSONデータ（辞書型）
        
    """
    
    url = dump_url.format(RDF_TYPE=rdf_type)
    return get_data(url, **kwargs)

def convert_to_dict(array, key='owl:sameAs'):
    """指定されたフィールドの値をキーとして、辞書型の配列を辞書型に変換する
    キーは一意であることが前提。同じキーが複数存在する場合はいずれか一つのみ格納される。
    
    Args:
        array: 配列
        key: 辞書型データのキーとする値
    
    Returns:
        dict: 変換された辞書型データ
    
    """
    
    data = {}
    for d in array:
        data[d[key]] = d
    
    return data

def summarize_by_key(data, summarize_key):
    """指定されたフィールドの値をキーとして、辞書型を階層構造に変換する
    
    Args:
        data: 辞書型データ
        summarize_key: 階層化する際に用いるキー
        
    Returns:
        dict: 階層化された辞書型データ
    
    """
    result = {}
    keys = data.keys()

    for key in keys:
        if summarize_key in data[key]:
            summarize_id = data[key][summarize_key]
        else:
            summarize_id = ''
        
        if not summarize_id in result.keys():
            result[summarize_id] = {}
    
        result[summarize_id][key] = data[key] 
    
    return result

def get_station(station_id, stations):
    """指定されたキーにマッチする駅情報を返す
    該当する値がstationsに格納されていない場合は、その駅が所属する路線の駅情報を
    APIで追加取得し、stationsに追加して返す（それでも見つからない場合はNoneを返す）
    
    Args:
        station_id: 駅の固有識別子
        stations: 取得済の駅情報
    
    Returns:
        dict: 駅情報
        ※stationsも更新される場合あり
        
    """
    
    # station_idに該当する値がstationsに格納されていない場合の処理
    if not station_id in stations:
        # 所属路線のIDを生成
        split_keys = station_id.split(':')[1].split('.')
        line_id = 'odpt.Railway:%s.%s' % (split_keys[0], split_keys[1])
        
        # 路線に含まれる駅を取得してstationsに追加する
        stations.update(get_query('Station', {'odpt:railway': line_id}))

    if not station_id in stations:
        return None

    return stations[station_id]

def get_days(date, holidays, specific_calendars = None):
    """指定された日の日付区分を返す
    この関数では優先度は考慮していないため、基本的に条件を満たす日付区分すべてを返す。
    
    基底クラスの判定条件については以下のとおり。
    ・曜日（日曜～土曜）：常にいずれか1つを返す
    ・休日：日曜日、または休日に該当する場合
    ・平日：月曜日～金曜日、かつ休日に該当しない場合
    ・土休日：土曜日、または休日の条件を満たす場合
    
    Args:
        date: 日付
        holidays: 休日を表す辞書型データ（jp_holiday.get_holidays()で取得）
        specific_calendars: odpt:Calendarの戻り値（特定クラスを判定したい場合）    
    
    Returns:
        array: 該当する日付区分の固有識別子
        
    """
    day = date.weekday()
    
    result = []
    
    # 曜日
    result.append(week[day])
    
    if day == 6 or jp_holiday.is_holiday(date, holidays):
        # 休日
        result.append('odpt.Calendar:Holiday')
        result.append('odpt.Calendar:SaturdayHoliday')
        
    elif day == 5:
        # 土休日
        result.append('odpt.Calendar:SaturdayHoliday')
            
    elif day < 5:
        # 平日
        result.append('odpt.Calendar:Weekday')
    
    day_str = date.strftime('%Y-%m-%d')
    
    # 特定日
    if not specific_calendars is None:
        for key in specific_calendars.keys():
            if not 'odpt:day' in specific_calendars[key].keys():
                continue
            
            if day_str in specific_calendars[key]['odpt:day']:
                result.append(key)
                continue
    
    return result