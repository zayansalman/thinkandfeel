import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px
import country_converter as coco
import numpy as np
cc = coco.CountryConverter()

geolocator = Nominatim(user_agent="geoapiExercises")

tnf_df = pd.read_excel('thinkandfeel.xlsx')
tnf_df['iso_a3'] = cc.pandas_convert(series=tnf_df['Country of Sale'], to='ISO3')
tnf_df['log_plays'] = np.log10(tnf_df['Quantity'])
# get most recent Reporting Date from tnf_df in a new variable
reporting_date = tnf_df['Reporting Date'].max()
# get total Quantity from tnf_df in a new variable
total_quantity = tnf_df['Quantity'].sum()
# get total Earnings from tnf_df in a new variable
total_earnings = tnf_df['Earnings (USD)'].sum()

# think and feel earnings by country
tnf_ce_df = tnf_df.groupby(['iso_a3']).sum().sort_values('Earnings (USD)', ascending=False).reset_index()
# Create an empty list to store the coordinates
coordinates = []

# Iterate over each row in the dataframe
for index, row in tnf_ce_df.iterrows():
    try:
        location = geolocator.geocode(row['iso_a3'], timeout=10)
        coordinates.append((location.latitude, location.longitude))
    except:
        # If the ISO 3 code is not found, append None
        coordinates.append((None, None))

# Add the coordinates as new columns in the dataframe
tnf_ce_df['latitude'] = [x[0] for x in coordinates]
tnf_ce_df['longitude'] = [x[1] for x in coordinates]

# top 10 countries by plays
top10_countries = tnf_ce_df.head()['iso_a3'].values
tnf_df.sort_values('Quantity', ascending=False, inplace=True)
top10_df = tnf_df[tnf_df['iso_a3'].isin(top10_countries)]
top10_df = top10_df.set_index('Reporting Date')
top10_df = top10_df.sort_index(ascending=True)

plays_fig = px.scatter(top10_df, x=top10_df.index, y='Quantity', color='iso_a3')

fig = px.choropleth(tnf_ce_df, locations='iso_a3',
                    locationmode='ISO-3',
                    color='log_plays',
                    hover_name="iso_a3",
                    hover_data=['Quantity', 'Earnings (USD)'],
                    color_continuous_scale='ylgn',
                    # range_color=(0, total_quantity * 2),
                    # title='Plays by Country',
                    width=1000, height=800,
                    labels={'Quantity': 'Plays', 'log_plays': 'Plays(log-scaled)'},
                    projection='natural earth')

fig.update_layout(autosize=True, geo=dict(bgcolor='rgba(0,0,0,0)'), showlegend=False)

st.set_page_config(page_title="think and feel", page_icon=None)

st.title("think and feel")
st.write('Analytics as of ' + str(reporting_date.date()))
st.metric(label='Total Plays:', value=str(total_quantity))
st.metric(label='Total Earnings:', value='$' + str(round(total_earnings)))

st.subheader('World map visualising plays')
st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    country_option = st.selectbox('Select a country', tnf_df['iso_a3'].unique())
    cpdf = tnf_df.loc[tnf_df['iso_a3'] == country_option]
    st.subheader('Plays by platform by country')
    platform_fig = px.pie(cpdf, values='Quantity', names='Store')
    st.plotly_chart(platform_fig, use_container_width=True)
with col4:
    st.subheader('Plays by top 5 countries over time')
    st.plotly_chart(plays_fig, use_container_width=True)
