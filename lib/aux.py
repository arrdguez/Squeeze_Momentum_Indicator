#!/usr/bin/python3

import requests 
import json
#import decimal
#import hmac
import time
import pandas as pd
#import hashlib
#from decimal import Decimal



import os.path



request_delay = 1000

class Binance:


  KLINE_INTERVALS = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']


  def __init__(self):

    self.base = 'https://api.binance.com'
    self.endpoints = {
      "klines"       : '/api/v3/klines',
    }

  def _get(self, url, params = None, headers = None) -> dict:
    """ Makes a Get Request """
    try: 
      response = requests.get(url, params=params, headers=headers)
      data = json.loads(response.text)
      data['url'] = url
    except Exception as e:
      print("Exception occured when trying to access "+url)
      print(e)
      data = {'code': '-1', 'url':url, 'msg': e}
    return data

  def GetSymbolKlinesExtra(self, symbol:str, interval:str, limit:int = 1000, end_time = False):
    # Basicall, we will be calling the GetSymbolKlines as many times as we need 
    # in order to get all the historical data required (based on the limit parameter)
    # and we'll be merging the results into one long dataframe.

    repeat_rounds = 0
    if limit > 1000:
      repeat_rounds = int(limit/1000)
    initial_limit = limit % 1000
    if initial_limit == 0:
      initial_limit = 1000
    # First, we get the last initial_limit candles, starting at end_time and going
    # backwards (or starting in the present moment, if end_time is False)
    df = self.GetSymbolKlines(symbol, interval, limit=initial_limit, end_time=end_time)
    while repeat_rounds > 0:
      # Then, for every other 1000 candles, we get them, but starting at the beginning
      # of the previously received candles.
      df2 = self.GetSymbolKlines(symbol, interval, limit=1000, end_time=df['time'][0])
      df = df2.append(df, ignore_index = True)
      repeat_rounds = repeat_rounds - 1
    
    return df

  def GetSymbolKlines(self, symbol:str, interval:str, limit:int = 1000, end_time = False):
    ''' 
    Gets trading data for one symbol 
    
    Parameters
    --
      symbol str:        The symbol for which to get the trading data

      interval str:      The interval on which to get the trading data
        minutes      '1m' '3m' '5m' '15m' '30m'
        hours        '1h' '2h' '4h' '6h' '8h' '12h'
        days         '1d' '3d'
        weeks        '1w'
        months       '1M;
    '''

    if limit > 1000:
      return self.GetSymbolKlinesExtra(symbol, interval, limit, end_time)
    
    params = '?&symbol='+symbol+'&interval='+interval+'&limit='+str(limit)
    if end_time:
      params = params + '&endTime=' + str(int(end_time))

    url = self.base + self.endpoints['klines'] + params

    # download data
    data = requests.get(url)
    dictionary = json.loads(data.text)

    # put in dataframe and clean-up
    df = pd.DataFrame.from_dict(dictionary)
    df = df.drop(range(6, 12), axis=1)

    # rename columns
    col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
    df.columns = col_names

    # transform values from strings to floats
    for col in col_names:
      df[col] = df[col].astype(float)

    df['date'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format=True)

    return df






def Main():

  exchange = Binance()


if __name__ == '__main__':
  Main()
