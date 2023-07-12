import geopandas as gpd
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import pydeck.data_utils as pdu

agebs = gpd.GeoDataFrame(pd.read_pickle('data/agebs.pkl'))
organizations = pd.read_pickle('data/organizations.pkl')
organization_demographics = pd.read_pickle('data/organization_demographics.pkl')
organization_profiles = pd.read_pickle('data/organization_profiles.pkl')
organization_regions = pd.read_pickle('data/organization_regions.pkl')

ods_labels = {
    'ods1': 'ODS 1',
    'ods2': 'ODS 2',
    'ods3': 'ODS 3',
    'ods4': 'ODS 4',
    'ods5': 'ODS 5',
    'ods6': 'ODS 6',
    'ods7': 'ODS 7',
    'ods8': 'ODS 8',
    'ods9': 'ODS 9',
    'ods10': 'ODS 10',
    'ods11': 'ODS 11',
    'ods12': 'ODS 12',
    'ods13': 'ODS 13',
    'ods14': 'ODS 14',
    'ods15': 'ODS 15',
    'ods16': 'ODS 16',
    'ods17': 'ODS 17',
}

ods_choice = st.selectbox(
    "Selecciona un ODS para visualizar:", [
        'ods1',
        'ods2',
        'ods3',
        'ods4',
        'ods5',
        'ods6',
        'ods7',
        'ods8',
        'ods8',
        'ods10',
        'ods11',
        'ods12',
        'ods13',
        'ods14',
        'ods15',
        'ods16',
        'ods17',
    ],
    format_func=lambda value: ods_labels[value])

org_with_regions = organizations \
    .dropna(subset=ods_choice) \
    .join(other=organization_regions.set_index('organization_name'), on='name') \
    .dropna(subset='sector_name') \
    .groupby(by=['sector_name']) \
    .agg({
    f'{ods_choice}': 'max',
    'name': lambda x: ' '.join(x.values)
}) \
    .join(other=agebs.set_index('sector_name'), on='sector_name')

# colors = {
#     'Relevancia 1': '[255, 255, 255]',
#     'Relevancia 2': '[255, 255, 255]',
#     'Relevancia 3': '[255, 255, 255]',
# }
# org_with_regions['color'] = org_with_regions[ods_choice].apply(lambda value: colors[value])
# st.write(gpd.GeoDataFrame(org_with_regions))

layers = [
    pdk.Layer(
        "GeoJsonLayer",
        data=gpd.GeoDataFrame(org_with_regions),
        get_fill_color='[255, 255, 255]',
        pickable=True,
    )
]

deck = pdk.Deck(
    layers,
    initial_view_state=pdk.ViewState(latitude=25.686613, longitude=-100.316116, zoom=10, max_zoom=16, min_zoom=10),
    tooltip={
        'html': '<b>{name}</b>',
    })
st.pydeck_chart(deck)
