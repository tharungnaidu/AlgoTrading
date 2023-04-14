# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 13:12:38 2023

@author: PRASHANTH
"""

# -- coding: utf-8 --
"""
Created on Fri Apr  7 14:47:46 2023

@author: PRASHANTH
"""

# -- coding: utf-8 --

from copy import copy
from fyers_api import fyersModel
from fyers_api import accessToken
#import test_config_app as config
import requests
import os
from time import sleep
import re
import urllib.parse as urlparse
import datetime as dt
import logging
import time
import requests
import pandas as pd
import numpy as np
import pyotp
import chromedriver_autoinstaller
from stocktrends import Renko
from selenium import webdriver
#chrome options class is used to manipulate various properties of Chrome driver
from selenium.webdriver.chrome.options import Options
#waits till the content loads
from selenium.webdriver.support.ui import WebDriverWait
#finds that content
from selenium.webdriver.support import expected_conditions as EC
#find the above condition/conntent by the xpath, id etc.
from selenium.webdriver.common.by import By
import copy
import statsmodels.api as sm



class config:
    client_id = 'XG13259'
    app_id = 'AI6EB88RLF-100'
    secret_key = 'IUX6DKFG5M'
    redirect_uri ='https://web.whatsapp.com/'
    response_type = 'code'
    grant_type = 'authorization_code'
    otp_key = 'PIY63PDVMAQMPZQU5O2I324F7FYQT4M5'
    pin = '1820'
def login():

    """Function to login using selenium and enter OTP and generate access token"""    

    PATH = chromedriver_autoinstaller.install(cwd=True)
    PATH = os.path.split(PATH)[0][-3:]+'/'+os.path.split(PATH)[1].rstrip('.exe')
    
    otp_auth = pyotp.TOTP(config.otp_key)
    
    # def login():
    session=accessToken.SessionModel(client_id=config.app_id,
        secret_key=config.secret_key,redirect_uri=config.redirect_uri, 
        response_type='code', grant_type='authorization_code')
    
    response = session.generate_authcode()
    
    options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    ex_path = os.getcwd().replace('\\','/')+'/'+PATH
    driver = webdriver.Chrome(executable_path=ex_path,options=options)
    driver.get(response)
    
    form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@type='text']")))
    driver.find_element_by_xpath("//input[@type='text']").send_keys(config.client_id)
    driver.find_element_by_xpath("//button[@id='clientIdSubmit']").click()
    

    
    form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="otp-container"]')))
    auth_key = [i for i in otp_auth.now()]
    driver.find_element_by_xpath("/html/body/section[6]/div[3]/div[3]/form/div[3]/input[1]").send_keys(auth_key[0])
    driver.find_element_by_xpath('/html/body/section[6]/div[3]/div[3]/form/div[3]/input[2]').send_keys(auth_key[1])
    driver.find_element_by_xpath('/html/body/section[6]/div[3]/div[3]/form/div[3]/input[3]').send_keys(auth_key[2])
    driver.find_element_by_xpath('/html/body/section[6]/div[3]/div[3]/form/div[3]/input[4]').send_keys(auth_key[3])
    driver.find_element_by_xpath('/html/body/section[6]/div[3]/div[3]/form/div[3]/input[5]').send_keys(auth_key[4])
    driver.find_element_by_xpath('/html/body/section[6]/div[3]/div[3]/form/div[3]/input[6]').send_keys(auth_key[5])
    
    driver.find_element_by_xpath("//button[@id='confirmOtpSubmit']").click()
    # sleep(5)
    
    pin = [i for i in config.pin]
    form = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="pin-container"]')))
    driver.find_element_by_xpath("/html/body/section[8]/div[3]/div[3]/form/div[2]/input[1]").send_keys(pin[0])
    driver.find_element_by_xpath("/html/body/section[8]/div[3]/div[3]/form/div[2]/input[2]").send_keys(pin[1])
    driver.find_element_by_xpath("/html/body/section[8]/div[3]/div[3]/form/div[2]/input[3]").send_keys(pin[2])
    driver.find_element_by_xpath("/html/body/section[8]/div[3]/div[3]/form/div[2]/input[4]").send_keys(pin[3])
    driver.find_element_by_xpath("//button[@id='verifyPinSubmit']").click()
    # form = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="interstitial-wrapper"]')))
    sleep(5)
    # form = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="interstitial-wrapper"]')))
    auth = driver.current_url
    parsed = urlparse.urlparse(auth)
    auth_code = urlparse.parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    access_token = response["access_token"]
    return access_token
def MACD(DF,a,b,c):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = DF.copy()
    df["MA_Fast"]=df["Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])

def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    #df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def slope(ser,n):
    "function to calculate the slope of n consecutive points on a plot"
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


def renko_DF(DF):
    
    "function to convert ohlc data into renko bricks"
    df = DF.copy()
 #   df = df.iloc[:,[0,1,2,3,4,5]]
    df.columns = ["date","open","close","high","low","volume"]
  
    
    df2 = Renko(df)
    
   
    df2.brick_size = round(ATR(DF,120)["ATR"].tolist()[-1],4)
    renko_df = df2.get_ohlc_data()
    renko_df["bar_num"] = np.where(renko_df["uptrend"]==True,1,np.where(renko_df["uptrend"]==False,-1,0))
    for i in range(1,len(renko_df["bar_num"])):
        if renko_df["bar_num"][i]>0 and renko_df["bar_num"][i-1]>0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
        elif renko_df["bar_num"][i]<0 and renko_df["bar_num"][i-1]<0:
            renko_df["bar_num"][i]+=renko_df["bar_num"][i-1]
    renko_df.drop_duplicates(subset="date",keep="last",inplace=True)
    return renko_df
def renko_merge(DF):
    "function to merging renko df with original ohlc df"
    df = copy.deepcopy(DF)
    renko = renko_DF(df)
    renko.columns = ["Date","open","high","low","close","uptrend","bar_num"]
    merged_df = df.merge(renko.loc[:,["Date","bar_num"]],how="outer",on="Date")
    merged_df["bar_num"].fillna(method='ffill',inplace=True)
    merged_df["macd"]= MACD(merged_df,12,26,9)[0]
    merged_df["macd_sig"]= MACD(merged_df,12,26,9)[1]
    merged_df["macd_slope"] = slope(merged_df["macd"],5)
    merged_df["macd_sig_slope"] = slope(merged_df["macd_sig"],5)
    return merged_df



def get_hist(client, symbol, period):
    
    """ To get Candlestic historic data
            Symbol should be of format 'NSE:NIFTY50-INDEX' or 'NSE"RELIANCE-EQ' or
            as in instruments['symbol']   -----  open variable initialized in line 236
    """
    
    per = str(period)
    today = dt.datetime.now()
    start = int((today - dt.timedelta(days=7)).timestamp())
    # start = start.strftime("%Y-%m-%d")
    end = int(today.timestamp())
    data = {
                "symbol" : symbol,
                "resolution" : per,
                "date_format" : "0",
                "range_from" : str(start),
                "range_to" : str(end),
                "cont_flag" : "0"
            }
    
    # return self.client.history(data)
    
    hist = client.history(data)
    df = pd.DataFrame(data=hist['candles'], columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Date'] = df['Date'].apply(lambda x: dt.datetime.fromtimestamp(x))
    # df = df.iloc[-80:]    
    return df
def trade_signal(MERGED_DF,l_s):
    "function to generate signal"
    signal = ""
    df = copy.deepcopy(MERGED_DF)
    if l_s == "":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Buy"
        elif df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Sell"
            
    elif l_s == "long":
        if df["bar_num"].tolist()[-1]<=-2 and df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close_Sell"
        elif df["macd"].tolist()[-1]<df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]<df["macd_sig_slope"].tolist()[-1]:
            signal = "Close"
            
    elif l_s == "short":
        if df["bar_num"].tolist()[-1]>=2 and df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Close_Buy"
        elif df["macd"].tolist()[-1]>df["macd_sig"].tolist()[-1] and df["macd_slope"].tolist()[-1]>df["macd_sig_slope"].tolist()[-1]:
            signal = "Close"
    print(f"hellllllllllllllllllllllllllllllllllllllllllllllllllllllllloooooooooooooooooooooo {signal}")
    return signal
    
pairs=['NSE:PNB-EQ','NSE:TATASTEEL-EQ','NSE:DISHTV-EQ','NSE:SJVN-EQ','NSE:TRIDENT-EQ']
# pairs = [    "NSE:TATAMOTORS-EQ",    "NSE:HINDUNILVR-EQ",    "NSE:RELIANCE-EQ",    "NSE:HDFCBANK-EQ",    "NSE:MARUTI-EQ",    "NSE:ICICIBANK-EQ",    "NSE:SBIN-EQ",    "NSE:INFY-EQ",    "NSE:AXISBANK-EQ",    "NSE:BAJAJFINSV-EQ",    "NSE:ONGC-EQ",    "NSE:TITAN-EQ",    "NSE:CIPLA-EQ",    "NSE:SUNPHARMA-EQ",    "NSE:BPCL-EQ",    "NSE:ITC-EQ",    "NSE:LT-EQ",    "NSE:HCLTECH-EQ",    "NSE:HEROMOTOCO-EQ",    "NSE:ULTRACEMCO-EQ",    "NSE:TCS-EQ",    "NSE:WIPRO-EQ",    "NSE:BAJAJ-AUTO-EQ",    "NSE:ADANIPORTS-EQ",    "NSE:ASIANPAINT-EQ",    "NSE:BAJFINANCE-EQ",    "NSE:BRITANNIA-EQ",    "NSE:COALINDIA-EQ",    "NSE:DRREDDY-EQ",    "NSE:EICHERMOT-EQ",    "NSE:GAIL-EQ",    "NSE:GRASIM-EQ",    "NSE:HDFCLIFE-EQ",    "NSE:HERITGFOOD-EQ",    "NSE:HINDALCO-EQ",    "NSE:HINDPETRO-EQ",    "NSE:INDUSINDBK-EQ",    "NSE:IOC-EQ",    "NSE:JSWSTEEL-EQ",    "NSE:KOTAKBANK-EQ",    "NSE:M&M-EQ",    "NSE:MARICO-EQ",    "NSE:NTPC-EQ",    "NSE:ONGC-EQ",    "NSE:POWERGRID-EQ",    "NSE:RELINFRA-EQ",    "NSE:SHREECEM-EQ",    "NSE:TECHM-EQ",    "NSE:UPL-EQ",    "NSE:VEDL-EQ",    "NSE:ZEEL-EQ"]
access_token = login() #consider modyfying the code such that it doesnt have to login for every 5 minutes
con = fyersModel.FyersModel(client_id=config.app_id, token=access_token, log_path='fyers_log/') #creating an connectionn with fyers
def main():
    try:
        print("starting after 5 mins")
        temp=con.positions()['netPositions'] #open_pos contains an list of dictionaries
        open_pos={}
        for rows in temp:
            open_pos[rows['symbol']]=rows['side']  #for side==1(long) and for side==-1(short)
        long_short=""
        for symbol in pairs:
            if symbol in open_pos.keys():
                if open_pos[symbol]==1:
                    long_short="long"
                elif open_pos[symbol]==-1:
                    long_short="short" #for short the symbol is -1
            ohlc=get_hist(con,symbol,5) #for the given symbol i am requesting an 5 minute candle
            
            signal=trade_signal(renko_merge(ohlc),long_short)
            data = {
                "symbol":symbol,
                "qty":1,
                "type":2, #markey order
                "side":1, #buy
                "productType":"INTRADAY",
                "limitPrice":0,
                "stopPrice":0,
                "validity":"DAY",
                "disclosedQty":0,
                "offlineOrder":"False",
            }
            if signal == "Buy":
                data['side']=1
                con.place_order(data=data)
                print("New long position initiated for ", symbol)
            elif signal == "Sell":
                data['side']=-1
                con.place_order(data=data)
                print("New short position initiated for ", symbol)
            elif signal == "Close":
                if open_pos[symbol]==1:
                    data['side']=-1
                    con.place_order(data=data)
                else:
                    data['side']=1
                    con.place_order(data=data)
                
            elif signal == "Close_Buy": #buy it twice
                
                print("Existing Short position closed for ", symbol)
                data['side']=1
                con.place_order(data=data)
                con.place_order(data=data)
                print("New long position initiated for ", symbol)
            elif signal == "Close_Sell":
                exit_id={"id":symbol}
                con.exit_positions(data=exit_id)
                data['side']=-1
                con.place_order(data=data)
                con.place_order(data=data)
                print("New short position initiated for ", symbol)
    except:
        print("error occured...so exception raised..........")
                
                
    




starttime=time.time()
timeout = time.time() + 60*60*4  # 60 seconds times 60 meaning the script will run for 1 hr
while time.time() <= timeout:
    print("passthrough at ",time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    main()
    time.sleep(360 - ((time.time() - starttime) % 360.0)) # 5 minute interval between each new execution
    
print("successful")
print(ll)
# Close all positions and exit


