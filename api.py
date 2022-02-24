import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import requests
import json
from datetime import datetime


st.title("COVID-19 World Symptoms Survey Open API Explorer")
# selection of type "multiple" for alt charts
multi = alt.selection_multi() 

# Get country list
def get_countries():
    response = requests.get("https://covidmap.umd.edu/api/country").text
    jsonData = json.loads(response)
    df_out = pd.DataFrame.from_dict(jsonData['data'])
    return df_out

# Get data function
def get_API_data(start, end, indicator, country):
    query = f"https://covidmap.umd.edu/api/resources?indicator={indicator}&type=daily&country={country}&daterange={start}-{end}"
    print(query)
    response = requests.get(query).text
    jsonData = json.loads(response)
    df_out = pd.DataFrame.from_dict(jsonData['data'])
    return df_out

# Make Chart
# In: data dataframe, pct column name, multi selector
# Returns chart fro specified pct columns name
def make_chart(df, pct, selector):
    data = df
    data.survey_date = pd.to_datetime(data["survey_date"])
    return alt.Chart(data.reset_index()).mark_line().encode(
        x='survey_date:T',
        y=f'{pct}:Q',
        color=alt.condition(selector, 'country:N', alt.value('lightgrey')),
        opacity=alt.condition(selector, alt.value(0.8), alt.value(0.1))
    ).add_selection(selector).interactive()

# -- start of sidebar --
st.sidebar.markdown('## UMD COVID-19 Open Data API Explorer')
start = st.sidebar.date_input("Start:")
end = st.sidebar.date_input("End:")

indicator = st.sidebar.multiselect('Select indicator', ['covid', 'flu', 'mask', 'contact', 'finance', 'anosmia', 'vaccine_acpt', 'covid_vaccine', 
                                            'trust_fam', 'trust_healthcare', 'trust_who', 'trust_govt', 'trust_politicians', 'twodoses',
                                            'concerned_sideeffects', 'hesitant_sideeffects', 'modified_acceptance', 'access_wash', 
                                            'wash_hands_24h_3to6', 'wash_hands_24h_7orMore', 'cmty_covid', 
                                            'hes_side_effects', 'hes_wontwork', 'hes_dontbelieve', 'hes_dontlike', 'hes_waitlater', 'hes_otherpeople',
                                            'hes_cost', 'hes_religious', 'hes_other', 'trust_doctors', 
                                            'barrier_reason_dontneed_alreadyhad', 'barrier_reason_dontneed_dontspendtime', 'barrier_reason_dontneed_nothighrisk', 
                                            'barrier_reason_dontneed_takeprecautions', 'barrier_reason_dontneed_notserious', 
                                            'barrier_reason_dontneed_notbeneficial', 'barrier_reason_dontneed_other', 'informed_access', 
                                            'appointment_have', 'appointment_tried', 'barrier_reason_government', 'work_outside_home_1d', 'shop_1d', 
                                            'restaurant_1d', 'spent_time_1d', 'large_event_1d', 'public_transit_1d', 'food_security', 'anxious_7d', 
                                            'depressed_7d', 'worried_become_ill'])

option = st.sidebar.checkbox("Select all countires")

if option:
    all_countries = get_countries().country.tolist()
else:
    country = st.sidebar.multiselect("Select countries", get_countries().country.tolist())

st.sidebar.markdown('Data from UMD COVID-19 World Survey Data [API](https://covidmap.umd.edu/api.html)')
# -- end of sidebar --


if start and end and indicator and option:
    df_list = []
    for c in all_countries:
        tmp_df = get_API_data(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), indicator[0], c)
        df_list.append(tmp_df)

    fin = pd.concat(df_list, ignore_index=True)
    print(fin)

    chart = make_chart(fin, fin.columns[0], multi)
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(fin)

elif start and end and indicator and country:
    print(start, end, indicator, country)

    df = get_API_data(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), indicator[0], country[0])
    if df.shape[0] == 0:
        st.write("No data, empty dataframe.")

    else:
        #--------------------
        # Charts
        #--------------------
        st.subheader("Results")

        if len(country) == 1:  
            chart = make_chart(df, df.columns[0], multi)
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(df)
        elif len(country) > 1:
            df_list = []
            for c in country:
                tmp_df = get_API_data(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"), indicator[0], c)
                df_list.append(tmp_df)

            fin = pd.concat(df_list, ignore_index=True)
            print(fin)

            chart = make_chart(fin, fin.columns[0], multi)
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(fin)
else:
    st.write("Something is missing! Check fields!")



