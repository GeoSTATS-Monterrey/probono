import geopandas as gpd
import pandas as pd
import streamlit as st
import pydeck as pdk
from pydeck.types import String

agebs = gpd.GeoDataFrame(pd.read_pickle('data/agebs.pkl'))
organizations = gpd.GeoDataFrame(pd.read_pickle('data/organizations.pkl'))
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

st.title("Mapa de organizaciones pro-bono")

active_modes = st.multiselect(
    'Selecciona la informacion de interes que quieres ver: ', [
        'Oficinas de organizaciones',
        'Actividad de organizaciones',
        'Año de incorporación legal',
        'Primer año de operaciones',
        'Ganancias anuales',
        'Cantidad de empleados',
        'Cantidad de voluntarios',
        'ODS'
    ],
    default=[
        'Oficinas de organizaciones',
        'Actividad de organizaciones'
    ],
)
# ods_choice = st.selectbox(
#     "Selecciona un ODS para visualizar:", [
#         'ods1',
#         'ods2',
#         'ods3',
#         'ods4',
#         'ods5',
#         'ods6',
#         'ods7',
#         'ods8',
#         'ods8',
#         'ods10',
#         'ods11',
#         'ods12',
#         'ods13',
#         'ods14',
#         'ods15',
#         'ods16',
#         'ods17',
#     ],
#     format_func=lambda value: ods_labels[value])


# org_with_regions = gpd.GeoDataFrame(organizations \
#                                     # .dropna(subset=ods_choice)
#                                     .join(other=organization_regions.set_index('organization_name'), on='name')
#                                     .dropna(subset='sector_name')
#                                     .groupby(by=['sector_name'])
#                                     .agg({
#     f'{ods_choice}': 'max',
#     'name': lambda x: ' '.join(x.values)
# }) \
#                                     .join(other=agebs.set_index('sector_name'), on='sector_name'))

# colors = {
#     'Relevancia 1': '[255, 255, 255]',
#     'Relevancia 2': '[255, 255, 255]',
#     'Relevancia 3': '[255, 255, 255]',
# }
# org_with_regions['color'] = org_with_regions[ods_choice].apply(lambda value: colors[value])
# st.write(gpd.GeoDataFrame(org_with_regions))

organization_sectors = gpd.GeoDataFrame(
    organizations
    .join(other=organization_regions.set_index('organization_name'), on='name')
    .dropna(subset=['sector_name', 'lon', 'lat'])
    .join(other=agebs.set_index('sector_name'), on='sector_name', lsuffix='organizations')
)

layers = []

if 'Oficinas de organizaciones' in active_modes:
    organizations_with_icons = organizations \
        .dropna(subset='address')
    organizations_with_icons['icon_data'] = None
    for i in organizations_with_icons.index:
        organizations_with_icons['icon_data'][i] = {
            'url': 'https://em-content.zobj.net/thumbs/240/apple/354/office-building_1f3e2.png',
            'width': 242,
            'height': 242,
            'anchorY': 242,
        }

    layers.append(
        pdk.Layer(
            "IconLayer",
            data=organizations_with_icons,
            get_icon='icon_data',
            get_size=4,
            size_scale=15,
            get_position=['lon', 'lat'],
            pickable=True,
        )
    )
if 'Actividad de organizaciones' in active_modes:
    organization_sectors['lon'] = organization_sectors.to_crs('+proj=cea').centroid.to_crs(organization_sectors.crs).x
    organization_sectors['lat'] = organization_sectors.to_crs('+proj=cea').centroid.to_crs(organization_sectors.crs).y
    layers.append(
        pdk.Layer(
            "HeatmapLayer",
            data=organization_sectors
            .filter(items=['lon', 'lat'])
            .dropna(subset=['lon', 'lat']),
            get_position=['lon', 'lat'],
            opacity=0.7,
            intensity=1,
            radius_pixels=100,
            threshold=0.3,
            aggregation='MEAN',
            get_weight=1,
        )
    )
if 'Ganancias anuales' in active_modes:
    organization_sectors['lon'] = organization_sectors.centroid.x
    organization_sectors['lat'] = organization_sectors.centroid.y
    layers.append(
        pdk.Layer(
            "ScreenGridLayer",
            data=organizations
            .filter(items=['annual_income', 'lon', 'lat']),
            get_position=['lon', 'lat'],
            get_weight='1',
            cell_size_pixels=20,
            opacity=0.4,
        )
    )

if 'Año de incorporación legal' in active_modes:
    organization_sectors['lon'] = organization_sectors.centroid.x
    organization_sectors['lat'] = organization_sectors.centroid.y
    H3_CLUSTER_LAYER_DATA = "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf.h3clusters.json"

    df = pd.read_json(H3_CLUSTER_LAYER_DATA)
    layers.append(
        pdk.Layer(
            "H3ClusterLayer",
            df,
            pickable=True,
            stroked=True,
            filled=True,
            extruded=False,
            get_hexagons="hexIds",
            get_fill_color="[255, (1 - mean / 500) * 255, 0]",
            get_line_color=[255, 255, 255],
            line_width_min_pixels=2,
        )
    )

deck = pdk.Deck(
    layers,
    initial_view_state=pdk.ViewState(latitude=25.686613, longitude=-100.316116, zoom=10, max_zoom=16, min_zoom=10),
    tooltip={
        'html': '<b>{name}</b>',
    })
st.pydeck_chart(deck)
