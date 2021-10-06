

import requests
import pandas as pd
import numpy as np
import datetime
import streamlit as st
import statsmodels.graphics.tsaplots as tsa_plots
from statsmodels.tsa.arima.model import ARIMA
from sqlalchemy import create_engine
import psycopg2 
import io
import os
from bs4 import BeautifulSoup

#Connection to server
con = psycopg2.connect(
            host ="ec2-3-218-47-9.compute-1.amazonaws.com",
            database="dadi8p16nf8hu6",
            user="xeveqgkrghuykv",
            password= "1b7f39571777c39375024da50622985ee602139a1189246b7773fc8d38693ab9")

cur = con.cursor()
def create_pandas_table(sql_query, database = con):
   table = pd.read_sql_query(sql_query, database)
   return table
df = create_pandas_table("SELECT date, rates FROM hyderabad_rates")#Dataframe created
cur.close()
con.close()
df.rates = pd.to_numeric(df.rates)
st.header('Welcome To The "Predictive Analytics On Poultry".')

st.subheader("FORECASTING OF THE BROILER RATES  FOR A WEEK")
#####################################################

##### Latest data import

url = "https://kiodigital.net/economy/hyderabad-chicken-price-today/"
r = requests.get(url)
soup=BeautifulSoup(r.text,"html.parser")
table = soup.find_all('table',attrs={'class':'table table-bordered'})


price = []
for div in table:
    rows = div.findAll('tr')
    for row in rows :
        price.append(row.findAll('td'))
live = str(price[4][2])
live = live.replace("<td><b>", "").replace("</b></td>", "").strip()
import re
temp = re.findall(r'\d+', live)
Rates = list(map(int, temp)) 
Rates=Rates[0]

latest = pd.DataFrame()
time = datetime.datetime.now()
time=time.strftime("20%y-%m-%d")
latest["date"]= [time]
latest["rates"]= [Rates] #Farmer_rate_per_kg


if (((df["date"].iloc[-1])!= (latest["date"])).bool()or((df["rates"].iloc[-1])!= (latest["rates"])).bool()):
     df= df.append(latest,ignore_index=True)
df['rates'].iloc[930]=139

###data export to server
#from sqlalchemy import create_engine
#import psycopg2 
#import io
#if you want to replace the table, we can replace it with normal to_sql method using headers from our df and then load the entire big time consuming df into DB.


engine = create_engine('postgresql+psycopg2://xeveqgkrghuykv:1b7f39571777c39375024da50622985ee602139a1189246b7773fc8d38693ab9@ec2-3-218-47-9.compute-1.amazonaws.com:5432/dadi8p16nf8hu6')
conn = engine.raw_connection()
cur = conn.cursor()
df.head(0).to_sql('hyderabad_rates', engine, if_exists='replace',index=False) #drops old table and creates new empty table
conn = engine.raw_connection()
cur = conn.cursor()
output = io.StringIO()
df.to_csv(output, sep='\t', header=False, index=False)
output.seek(0)
contents = output.getvalue()
cur.copy_from(output, 'hyderabad_rates', null="") # null values become ''
conn.commit()
cur.close()
conn.close()
st.success("Data Updated Successfully")

st.write('Please press the "predict" button')

if st.button("predict"): #Button for run the ARIMA model
  
   df=df.set_index('date')
   df.index = pd.to_datetime(df.index)
   df.rates = pd.to_numeric(df.rates)
   model1 = ARIMA(df.rates, order = (1,1,7))
   res1 = model1.fit()
   start_index = len(df)
   end_index = start_index + 6
   forecast = res1.predict(start=start_index, end=end_index)
   prediction= forecast.to_frame()
   prediction.reset_index(level=0,inplace=True)# converting index to column
   prediction = prediction.rename(columns={'index':'date','predicted_mean':'price'})
   a=datetime.datetime.now()
   from datetime import datetime, timedelta
  
   time1 = a+timedelta(1)
   time1=time1.strftime("20%y/%m/%d")
   time2= a+timedelta(7)
   time2=time2.strftime("20%y/%m/%d")
  
   Range= pd.date_range(start=time1,end= time2, freq='D')
   Range = Range.strftime("%d-%m-20%y")
   prediction['date']=Range
   result = prediction
   st.write(result)
   from plotly import graph_objs as go
   def plot_forecast_data():
       fig = go.Figure()
       fig.add_trace(go.Scatter(x=result['date'], y=result['price'], name="forecast"))
     #fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
       fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
       st.plotly_chart(fig)
   #def plot_forecast_data1():
       
   plot_forecast_data()
   