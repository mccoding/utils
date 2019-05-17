import arrow
import numpy as np
import pandas as pd

from const import datetime as datetime_const


def time_local_2_date(time_local: str) -> str:
  """parse nginx log time_local to dashed date

  TODO: shall make use of Asia/Shanghai directly
  """
  return arrow.get(time_local, 'DD/MMM/YYYY:HH:mm:ss Z').strftime('%Y-%m-%d')


def time_local_2_time(time_local: str) -> arrow.Arrow:
  """parse nginx log time_local to arrow object

  TODO: shall make use of Asia/Shanghai directly
  """
  return arrow.get(time_local, 'DD/MMM/YYYY:HH:mm:ss Z')


def target_time_is_today_or_yesterday(target_time: str) -> [bool, str]:
  """Parse the target time and check if is today or yesterday"""
  now = arrow.now()
  today = now.date()
  yesterday = now.replace(days=-1).date()
  target = arrow.get(target_time, 'YYYYMMDD')
  target_time_dash = target.format('YYYY-MM-DD')
  target_date = target.date()
  return today == target_date or yesterday == target_date, target_time_dash


def target_time_is_today(target_time: str) -> [bool, str]:
  """Parse the target time and check if is today"""
  now = arrow.now()
  today = now.date()
  target = arrow.get(target_time, 'YYYYMMDD')
  target_time_dash = target.format('YYYY-MM-DD')
  target_date = target.date()
  return today == target_date, target_time_dash


def parse_range(start_date: str,
                end_date: str,
                exclude: list = []) -> [bool, str]:
  """Parse the range and check whether today or yesterday is within the range

  Args:
    start_date: target start date, i.e. 20170602
    end_date: target end date, i.e. 20170604,
    exclude: if today or yesterday are included, make it None
  Returns:
    (today, yesterday) if today or yesterday within the range, else (None, None)
  """
  start = arrow.get(start_date, datetime_const.URL_DATE_FORMAT).date()
  end = arrow.get(end_date, datetime_const.URL_DATE_FORMAT).date()

  today = arrow.now()
  yesterday = today.replace(days=-1)

  if start <= today.date() <= end:
    today = today.format(datetime_const.REDIS_DATE_FORMAT)
    if today in exclude:
      today = None
  else:
    today = None

  if start <= yesterday.date() <= end:
    yesterday = yesterday.format(datetime_const.REDIS_DATE_FORMAT)
    if yesterday in exclude:
      yesterday = None
  else:
    yesterday = None

  return today, yesterday


def date_str_plus_one_day(origin_date: str, with_dash: bool = False):
  """Plus one day to the date string

  Args:
    origin_date: YYYYMMDD
    with_dash: if True, origin_date should be YYYY-MM-DD
  Returns:
    YYYYMMDD, one day after origin_date
  """
  if with_dash:
    date_format = datetime_const.REDIS_DATE_FORMAT
  else:
    date_format = datetime_const.URL_DATE_FORMAT
  return (arrow
          .get(origin_date, date_format)
          .replace(days=1)
          .format(date_format))


def populate_dates(start_date: str, end_date: str) -> np.ndarray:
  """populate the missing dates between start_date & end_date"""
  return (pd
          .date_range(start_date, end_date)
          .strftime(datetime_const.PYTHON_DATE_FORMAT))


def iter_dataframe_by_chunk(df, chunk=1):
  """Iterate DataFrame as DataFrame"""
  for i in range(0, df.shape[0], chunk):
    yield df[i:i + chunk]


def calculate_time_span(ts: list, discard: int = None) -> float:
  """Calculate the time interval sum of the given timestamp series, in minutes

  Args:
    ts: list of datetime object
    discard: discard interval which bigger than it (in minutes)
  """
  if len(ts) < 2:
    return 0.0

  span = 0.0
  ts.sort()
  for i, _ in enumerate(ts[:-1]):
    interval = (ts[i + 1] - ts[i]).seconds / 60
    if discard is not None and interval > discard:
      continue
    span += interval
  return span


def str_bool(input_str: str) -> bool:
  """Return True if the string representation indicates true values"""
  return input_str.lower() in ['true', 't', 'yes', 'y']


def float_comma(input_str: str) -> list:
  """Return comma separated string as list of float"""
  return [float(i) for i in input_str.split(',')]


def int_comma(input_str: str) -> list:
  """Return comma separated string as list of int"""
  return [int(i) for i in input_str.split(',')]


def display_rmb(fen: int):
  """把 分 为单位的金额显示为 元, 并保留2位小数

  Args:
    fen: 单位为分的整数
  """
  return round(float(fen) / 100, 2)


def grouped(iterable, n):
  """s -> (s0,s1,s2,...sn-1),
          (sn,sn+1,sn+2,...s2n-1),
          (s2n,s2n+1,s2n+2,...s3n-1),
          ...
  """
  return zip(*[iter(iterable)] * n)


def get_today_and_yesterday_date() -> tuple:
  """返回(今天, 昨天)的日期"""
  now = arrow.now()
  return (now.strftime(datetime_const.PYTHON_DATE_FORMAT),
          now.replace(days=-1).strftime(datetime_const.PYTHON_DATE_FORMAT))


def get_consecutive_days(df, start_date: arrow, end_date: arrow):
  '''返回df中最大连续天数'''
  max_date = (pd.DataFrame([dt.format(datetime_const.REDIS_DATE_FORMAT) 
                          for dt in arrow.Arrow.range('day', start_date , end_date)],
                          columns=['date'])
                .append(df.astype(str), sort=False)
                .drop_duplicates(keep=False)
                .date
                .max())
  max_date = arrow.get(max_date, datetime_const.REDIS_DATE_FORMAT).shift(days=1)
  consecutive_days = (end_date - max_date).days + 1
  return consecutive_days if consecutive_days > 0 else 0
