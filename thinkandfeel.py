import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px
import country_converter as coco
cc = coco.CountryConverter()

geolocator = Nominatim(user_agent="geoapiExercises")

tnf_df = pd.read_excel('thinkandfeel.xlsx')
tnf_df['iso_a3'] = cc.pandas_convert(series=tnf_df['Country of Sale'], to='ISO3')
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

fig = px.scatter_geo(tnf_ce_df, locations='iso_a3', locationmode='ISO-3',
                     color='Quantity', hover_name='iso_a3', size='Quantity',
                     title='Value by country',
                     projection='natural earth')

st.title("think and feel")
st.write('Analytics as of ' + str(reporting_date.date()))
st.write('Total Plays:  ' + str(total_quantity))
st.write('Total Earnings: $' + str(round(total_earnings)))
st.plotly_chart(fig)
