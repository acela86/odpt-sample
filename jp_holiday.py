# -*- coding: utf-8 -*-

# 祝日判定ライブラリ

import csv
import requests
from datetime import datetime

# 祝日データのURL（内閣府）
holiday_url = r'http://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv'

def get_holidays():
    """祝日データを取得する
    
    Returns:
        dict: 辞書型データ（キー: 日付（YYYYmmdd） 値: 名称）
    
    """
    
    # データのダウンロード
    response = requests.get(holiday_url, timeout=3)
    response.raise_for_status()
    
    # CSVとして読み込み
    reader = csv.reader(response.content.decode('shift_jis').splitlines(), \
                        delimiter=',')
    
    # ヘッダ行の読み飛ばし
    header = next(reader)
    
    # 辞書型データの生成
    holidays = {}
    for line in reader:
        date = datetime.strptime(line[0], '%Y/%m/%d').strftime('%Y%m%d')
        
        holidays[date] = line[1]

    return holidays
    
def is_holiday(date, holidays):
    """祝日かどうかを判定する
    
    Args:
        date: 日付（datetime）
        holidays: get_holidays()で取得した祝日データ
    
    Returns:
        bool: 祝日かどうか
    
    """
        
    date_str =  date.strftime('%Y%m%d')
    return (date_str in holidays)

