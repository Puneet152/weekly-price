# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 09:02:05 2021

@author: khare
"""



import requests
import pandas as pd
import numpy as np
import datetime
import seaborn as sns
from selenium import webdriver
import streamlit as st
import statsmodels.graphics.tsaplots as tsa_plots
from statsmodels.tsa.arima.model import ARIMA
import os

option = webdriver.ChromeOptions()

# You will need to specify the binary location for Heroku 
option.binary_location = os.getenv('GOOGLE_CHROME_BIN')

option.add_argument("--headless")
option.add_argument('--disable-gpu')
option.add_argument('--no-sandbox')
option.add_argument("--disable-dev-shm-usage")

path="complete.csv"

st.header('POULTRY CHICKEN RATE FORECASTING FOR A WEEK')

st.header("weekly rates")

st.write("press the button")
if st.button("predict"):
   df=pd.read_csv(path)
   driver = webdriver.Chrome(executable_path=os.getenv('CHROME_EXECUTABLE_PATH'), options=option)
   driver.get('http://www.tsapbcc.com/')
   Path = '/html/body/div[3]/div/div[2]/div[2]/div/section/ul/li[5]/table/tbody/tr[4]/td[2]'
   rates=driver.find_element_by_xpath(Path).text
   rates=float(rates)
   rates=int(rates)
   latest = pd.DataFrame()
   time = datetime.datetime.now()
   time=time.strftime("20%y-%m-%d")
   latest["Date"]= [time]
   latest["Rates"]= [rates] #Farmer_rate_per_kg
   if ((df["Date"].iloc[-1])!= (latest["Date"])).bool():
               df= df.append(latest,ignore_index=True)
   df['Rates'].iloc[930]=139
   df.to_csv(path, index=False)
   data = pd.read_csv(path,index_col="Date",parse_dates=True)
   #data = data.fillna(data.mean()) # replace NA values with mean value 

   model1 = ARIMA(data.Rates, order = (1,1,7))
   res1 = model1.fit()
   start_index = len(data)
   end_index = start_index + 6
   forecast = res1.predict(start=start_index, end=end_index)
   prediction= forecast.to_frame()
   prediction.reset_index(level=0, inplace=True)# converting index to column
   from datetime import datetime,date
   prediction = prediction.rename(columns={'index':'date','predicted_mean':'price'})
   prediction['date']=prediction['date'].dt.strftime("%Y-%m-%d")
   result = prediction
   st.write(result)
   data2 =pd.read_csv(path)
   from plotly import graph_objs as go
   def plot_forecast_data():
       fig = go.Figure()
       fig.add_trace(go.Scatter(x=result['date'], y=result['price'], name="forecast"))
       fig.add_trace(go.Scatter(x=data2['Date'], y=data2['Rates'], name="actual_rates"))
       fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
       st.plotly_chart(fig)
   #def plot_forecast_data1():
       
   plot_forecast_data()
   

   
#reahe data fro
           #st.write(result) #display the data  
     #max_dat