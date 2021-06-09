#!/usr/bin/python3


import pandas as pd


from aux import Binance
from finta import TA


import numpy as np
from sklearn.linear_model import LinearRegression



class smiHistogram():
  """docstring for smiHistogram"""
  def __init__(self, 
           lengthKC:int = 20, 
             export:bool = False,
             kLinelenght:int = 1000):
    
    self.setupConfig = {
      "lengthKC" : lengthKC,
      'export' : export
    }




  def SMIH(self, df):
    length = self.setupConfig['lengthKC']
    dfTem = pd.DataFrame()
    dfTem['close'] = df['close']
    dfTem['sma'] =  df['close'].rolling(window = length).mean()
    dfTem['highest'] = df["high"].rolling(center=False, window = length).max()
    dfTem['lowest'] = df["low"].rolling(center=False, window = length).min()
    dfTem['aveHL'] = (dfTem['lowest'] + dfTem['highest'])/2
    dfTem['aveHLS'] = (dfTem['aveHL'] + dfTem['sma'])/2
    dfTem['source'] = df['close'] - dfTem['aveHLS']
    dfTem = dfTem.fillna(0)

    yAll = dfTem['source'].values.tolist()
    x = np.array(list(range(1, length+1))).reshape((-1, 1))

    SMH = []
    print(x)
    #exit()
    for i in range(999,length*2,-1):
      y = np.array(yAll[i-length+1:i+1])

      reg = LinearRegression(fit_intercept = True).fit(x, y)
      SMH.append(reg.predict(x)[-1 ])

    tmp = [0 for _ in range(41)]
    SMH = SMH + tmp
    SMH.reverse()
    dfTem['SMH'] = SMH
    print(dfTem)
    if self.setupConfig['export']:
      print("Exporting data ...")
      dfTem.to_csv("./dfTem.csv", sep='\t')
      df.to_csv("./df.csv", sep='\t')

    return SMH


  def ADX(self, df):
    print("Calculating ...")

    temporatDF = pd.DataFrame()
    temporatDF = df
    period = 14
    adxlen = 14


    for i in range(1, len(df['close'])):
      temporatDF['up'] = df['high'].diff()
      temporatDF['down'] = -df['low'].diff()
      temporatDF['up'] = temporatDF['up'].fillna(0)
      temporatDF['down'] = temporatDF['down'].fillna(0)



    print("up" + str(temporatDF.loc[len(temporatDF['up'])-1,'up']) + "\t" + str(temporatDF.loc[len(temporatDF['up'])-2,'up']))
    print("down" + str(temporatDF.loc[len(temporatDF['down'])-1,'down']) + "\t" + str(temporatDF.loc[len(temporatDF['down'])-2,'down']))


    df['TR'] = TA.TR(df)

    temporatDF['truerange'] = TA.SMMA( df, period = 14, column = "TR", adjust = True)

    print("truerange" + str(temporatDF.loc[len(temporatDF['truerange'])-1,'truerange']) + "\t" + str(temporatDF.loc[len(temporatDF['truerange'])-2,'truerange']))

    for i in range(0, len(df['close'])):
      if temporatDF.loc[i,"up"] > temporatDF.loc[i,"down"] and temporatDF.loc[i,"up"] > 0:
        temporatDF.loc[i, 'plus'] = temporatDF.loc[i, 'up'] # / temporatDF.loc[i, 'truerange']
        #temporatDF.loc[i, 'plus'] = temporatDF.loc[i, 'plus']
      else:
        temporatDF.loc[i, 'plus'] = 0

      if temporatDF.loc[i,"down"] > temporatDF.loc[i,"up"] and temporatDF.loc[i,"down"] > 0:
        temporatDF.loc[i, 'minus'] = temporatDF.loc[i, 'down'] #/ temporatDF.loc[i, 'truerange']
        #temporatDF.loc[i, 'minus'] = temporatDF.loc[i, 'minus']
      else:
        temporatDF.loc[i, 'minus'] = 0

    temporatDF['plus'] = temporatDF['plus'].fillna(0)
    temporatDF['minus'] = temporatDF['minus'].fillna(0)
    
    temporatDF['plus'] = TA.SMMA(temporatDF, period=14, column='plus', adjust=True)
    temporatDF['minus'] = TA.SMMA(temporatDF, period=14, column='minus', adjust=True)
    
    temporatDF['plus'] = 100 * temporatDF['plus'] / temporatDF['truerange']
    temporatDF['minus'] = 100 * temporatDF['minus'] / temporatDF['truerange']

    print("plus  " + str(temporatDF.loc[len(temporatDF['plus'])-1,'plus']) + "\t" + str(temporatDF.loc[len(temporatDF['plus'])-2,'plus']))
    print("minus " + str(temporatDF.loc[len(temporatDF['minus'])-1,'minus']) + "\t" + str(temporatDF.loc[len(temporatDF['minus'])-2,'minus']))

    temporatDF['sum'] = temporatDF['minus'] + temporatDF['plus']

    for i in range(0, len(temporatDF['sum'])):
      if float(temporatDF.loc[i,'sum']) == 0:
        temporatDF.loc[i,'tmp'] = abs(temporatDF.loc[i,'plus'] - temporatDF.loc[i,'minus']) / 1
      else:
        temporatDF.loc[i,'tmp'] = abs(temporatDF.loc[i,'plus'] - temporatDF.loc[i,'minus']) / temporatDF.loc[i,'sum'] 

    print(temporatDF['tmp'])
    temporatDF['ADX'] =100 * TA.SMMA(temporatDF, period=adxlen, column='tmp', adjust=True)
    print(temporatDF['tmp'])
    return(temporatDF['ADX'])

"""
adx(dilen, adxlen) => 
  [plus, minus] = dirmov(dilen)
  sum = plus + minus
  adx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)
  [adx, plus, minus]
"""

def main():

  #The next code was created to test 
  exchange = Binance()
  df = exchange.GetSymbolKlines("BTCUSDT", "1w")
  smi = smiHistogram(export = True)
  #smi.SMIH(df)
  smi.ADX(df)
  #print(df)




if __name__ == "__main__":
    main()