import streamlit as st
import pandas as pd
import numpy as np
from glob import glob
import streamlit.components.v1 as components
import altair as alt

st.title('VCU & Blue Physics Latency QA analysis')

listofbpfiles = glob('vcutrip2VRlatency*.csv')

filenow =  st.selectbox('Select Blue Physics File', listofbpfiles)

@st.cache_data
def generatebpdf(filenow):
    df = pd.read_csv(filenow, skiprows=4)
    timefirstbeamon = df.loc[df.linacon > 4, "time"].min()
    timelastbeamon = df.loc[df.linacon > 4, 'time'].max()
    zeros =  df.loc[(df.time<timefirstbeamon - 0.5) | (df.time>timelastbeamon + 0.5), 'ch0':].mean()
    dfzeros = df.loc[:,'ch0':] - zeros
    dfzeros.columns = ['sensor', 'cerenkov']
    df = pd.concat([df, dfzeros], axis=1)
    df['dose'] = (df.sensor - df.cerenkov * 0.95346993) * 0.2262186
    df['beamon'] = df.linacon/10
    starttimes = df.loc[df.linacon.diff() > 4, 'time'].to_list()
    finishtimes = df.loc[df.linacon.diff() < -4, 'time'].to_list()

    #remove acrs
    for s, f in zip(starttimes[1:], finishtimes[:-1]):
        if s-f < 0.5:
            starttimes.remove(s)
            finishtimes.remove(f)

    #Draw starttimes and finishtimes
    for i in range(len(starttimes)):
        df.loc[(df.time > starttimes[i] - 0.1) & (df.time < finishtimes[i] + 0.1), 'cycle'] = i + 1

    #Find gantry
    gantrystarts = [starttimes[0]]
    gantryfinish = []
    for s, f in zip(starttimes[1:], finishtimes[:-1]):
        if s - f > 10:
            gantrystarts.append(s)
            gantryfinish.append(f)
    gantryfinish.append(finishtimes[-1])

    return df

df = generatebpdf(filenow)
  
fig0 = alt.Chart(df).mark_line().encode(x='time', y='dose').interactive()


st.altair_chart(fig0)

