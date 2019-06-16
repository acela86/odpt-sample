# -*- coding: utf-8 -*-

### 日付区分判定のテストプログラム

import io
import sys
import datetime

import odpt_api
import jp_holiday

try:
    env = get_ipython().__class__.__name__
except NameError:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

holidays = jp_holiday.get_holidays()

year = 2019
date = datetime.date(year, 1, 1)

while (date.year == year):
    days = [s.split(':')[-1] for s in odpt_api.get_days(date, holidays)]
    
    print('%s: %s' % (date.strftime('%Y/%m/%d'), ','.join(days)))
    date += datetime.timedelta(1)