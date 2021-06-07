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
    last = len(df['close'])-1
    def getCDM(df):
      dmpos = df["high"][last-1] - df["high"][last-2]
      dmneg = df["low"][last-2] - df["low"][last-1]
      if dmpos > dmneg:
        return dmpos
      else:
        return dmneg 

    def getDMnTR(df):
      DMpos = []
      DMneg = []
      TRarr = []
      n = round(len(df)/14)
      idx = n
      while n <= (len(df)):
        dmpos = df["high"][n-1] - df["high"][n-2]
        dmneg = df["low"][n-2] - df["low"][n-1]
            
        DMpos.append(dmpos)
        DMneg.append(dmneg)
        
        a1 = df["high"][n-1] - df["high"][n-2]
        a2 = df["high"][n-1] - df["close"][n-2]
        a3 = df["low"][n-1] - df["close"][n-2]
        TRarr.append(max(a1,a2,a3))

        n = idx + n
      print(TRarr)
      return DMpos, DMneg, TRarr

    def getDI(df):
      DMpos, DMneg, TR = getDMnTR(df)
      CDM = getCDM(df)
      POSsmooth = (sum(DMpos) - sum(DMpos)/len(DMpos) + CDM)
      NEGsmooth = (sum(DMneg) - sum(DMneg)/len(DMneg) + CDM)
        
      DIpos = (POSsmooth / (sum(TR)/len(TR))) *100
      DIneg = (NEGsmooth / (sum(TR)/len(TR))) *100

      return DIpos, DIneg

    def getADX(df):
      DIpos, DIneg = getDI(df)
      dx = (abs(DIpos- DIneg) / abs(DIpos + DIneg)) * 100
        
       
      ADX = dx/14
      return ADX

    return(getADX(df))



def main():

  #The next code was created to test 
  exchange = Binance()
  df = exchange.GetSymbolKlines("BTCUSDT", "1h")
  smi = smiHistogram(export = True)
  #smi.SMIH(df)
  print(smi.ADX(df))
  #print(df)




if __name__ == "__main__":
    main()