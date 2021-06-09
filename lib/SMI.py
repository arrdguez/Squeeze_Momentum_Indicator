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

#plus = fixnan(100 * rma(up > down and up > 0 ? up : 0, len) / truerange)
#  minus = fixnan(100 * rma(down > up and down > 0 ? down : 0, len) / truerange)

    for i in range(0, len(df['close'])):

      if temporatDF.loc[i,"up"] > temporatDF.loc[i,"down"] and temporatDF.loc[i,"up"] > 0:
        temporatDF.loc[i, 'plus'] = temporatDF.loc[i, 'up'] / temporatDF.loc[i, 'truerange']
        temporatDF.loc[i, 'plus'] = temporatDF.loc[i, 'plus']
        temporatDF['plus'] = temporatDF['plus'].fillna(0)
      else:
        temporatDF.loc[i, 'plus'] = 0

      
      if temporatDF.loc[i,"down"] > temporatDF.loc[i,"up"] and temporatDF.loc[i,"down"] > 0:
        temporatDF.loc[i, 'minus'] = temporatDF.loc[i, 'down'] / temporatDF.loc[i, 'truerange']
        temporatDF.loc[i, 'minus'] = temporatDF.loc[i, 'minus']
        temporatDF['minus'] = temporatDF['minus'].fillna(0)
      else:
        temporatDF.loc[i, 'minus'] = 0
    temporatDF['plus'] = TA.SMMA(temporatDF, period=14, column='plus', adjust=True)
    temporatDF['minus'] = TA.SMMA(temporatDF, period=14, column='minus', adjust=True)
    
    print("plus  " + str(temporatDF.loc[len(temporatDF['plus'])-1,'plus']) + "\t" + str(temporatDF.loc[len(temporatDF['plus'])-2,'plus']))
    print("minus " + str(temporatDF.loc[len(temporatDF['minus'])-1,'minus']) + "\t" + str(temporatDF.loc[len(temporatDF['minus'])-2,'minus']))


    print(temporatDF)



  def tmp_ADX(self, df):
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
  smi.ADX(df)
  #print(df)




if __name__ == "__main__":
    main()