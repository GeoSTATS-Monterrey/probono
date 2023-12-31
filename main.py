import geopandas as gpd
import pandas as pd
import streamlit as st
import pydeck as pdk

agebs = gpd.GeoDataFrame(pd.read_pickle('data/agebs.pkl'))
sectors = agebs.dissolve(by='sector_name')
organizations = gpd.GeoDataFrame(pd.read_pickle('data/organizations.pkl'))
organization_demographics = pd.read_pickle('data/organization_demographics.pkl')
organization_profiles = pd.read_pickle('data/organization_profiles.pkl')
organization_sector_names = pd.read_pickle('data/organization_sectors.pkl')

excluded_orgs = [
    'geostats',
    'asdf',
]

organizations = organizations[~organizations.name.isin(excluded_orgs)]
organization_sector_names = organization_sector_names[~organization_sector_names.isin(excluded_orgs)]

organization_sector_count = organization_sector_names \
    .groupby(by='organization_name') \
    .count() \
    .sector_name

volunteer_ranges = {
    '0': 0,
    '1 a 5': 3,
    '6 a 10': 7,
    '11 a 20': 15,
    '21 a 50': 35,
    '51 a 100': 75,
    '101 a 250': 175,
    '251 a 500': 375,
    'Más de 500': 600,
}

organizations = organizations \
    .join(other=organization_sector_count, on='name') \
    .rename(columns={
    'sector_name': 'sector_count'
}) \
    .assign(per_sector_volunteers=organizations
            .volunteer_count
            .apply(lambda x: volunteer_ranges[x])
            .astype('float'))

organizations = organizations \
    .assign(per_sector_volunteers=organizations.per_sector_volunteers / organizations.sector_count)

organization_sectors = gpd.GeoDataFrame(
    organization_sector_names
    .join(other=sectors, on='sector_name', how='inner')
    .join(other=organizations.set_index('name'), on='organization_name', how='inner', rsuffix='_org')
)
organization_sectors[['x', 'y']] = organization_sectors \
    .to_crs('+proj=cea') \
    .centroid \
    .to_crs(agebs.crs) \
    .get_coordinates()

organization_agebs = gpd.GeoDataFrame(
    organization_sector_names
    .join(other=agebs.set_index('sector_name'), on='sector_name', how='inner')
)
organization_agebs[['x', 'y']] = organization_agebs \
    .to_crs('+proj=cea') \
    .centroid \
    .to_crs(agebs.crs) \
    .get_coordinates()

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

primary_color = [255, 75, 75]

st.title("Mapa de organizaciones pro-bono")

active_modes = st.multiselect(
    'Selecciona la información de interés que quieres ver: ', [
        'Oficinas de organizaciones',
        'Actividad de organizaciones',
        'Sectores',
        'Sectores por organización',
        'Distribución de voluntarios por sector',
        'Primer año de operaciones',
        'Ganancias anuales',
        'Cantidad de empleados',
        'Cantidad de voluntarios',
        'ODS'
    ],
    default=[
        'Oficinas de organizaciones',
        'Actividad de organizaciones',
        'Sectores',
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

# organization_sectors = gpd.GeoDataFrame(
#     organizations
#     .join(other=organization_regions
#           .dropna(subset='sector_name')
#           .set_index('organization_name'), on='name')
# .dropna(subset=['sector_name'])
# .join(other=agebs.set_index('sector_name'), on='sector_name', lsuffix='organizations')
# )


filtered_sectors = sectors

layers = []

if 'Distribución de voluntarios por sector' in active_modes:
    sector_volunteers = organization_sectors \
        .filter(items=['sector_name', 'per_sector_volunteers']) \
        .groupby('sector_name') \
        .sum()
    sectors = sectors.join(other=sector_volunteers)
    sectors = sectors.assign(tooltip_text=sectors.index)
    layers.append(
        pdk.Layer(
            "GeoJsonLayer",
            data=sectors
            .filter(items=['geometry', 'per_sector_volunteers', 'tooltip_text'])
            .dropna(subset='per_sector_volunteers'),
            opacity=0.8,
            extruded=True,
            get_fill_color=[255, 255, 64],
            get_elevation='per_sector_volunteers * 200',
            pickable=True,
        )
    )
if 'Sectores por organización' in active_modes:
    selected_org = st.selectbox(
        'Organización a visualizar:',
        organizations.name
    )
    filtered = gpd.GeoDataFrame(
        organization_sectors[organization_sectors['organization_name'] == selected_org]
        .filter(items=['geometry', 'sector_name'])
    )

    filtered_sectors = filtered_sectors[~filtered_sectors.index.isin(filtered)]

    layers.append(
        pdk.Layer(
            "GeoJsonLayer",
            data=filtered,
            get_fill_color=primary_color,
            opacity=0.5
        )
    )
if 'Sectores' in active_modes:
    layers.append(
        pdk.Layer(
            "GeoJsonLayer",
            data=filtered_sectors
            .assign(tooltip_text=sectors.index),
            get_fill_color=[128, 128, 128],
            opacity=0.2,
            pickable=True,
        )
    )
if 'Oficinas de organizaciones' in active_modes:
    organizations_with_icons = organizations \
        .dropna(subset='address')
    organizations_with_icons['icon_data'] = None
    for i in organizations_with_icons.index:
        organizations_with_icons['icon_data'][i] = {
            'url': 'https://raw.githubusercontent.com/GeoSTATS-Monterrey/probono/main/icons/office-building_1f3e2.png',
            'width': 128,
            'height': 128,
            'anchorY': 128,
        }
    layers.append(
        pdk.Layer(
            "IconLayer",
            data=organizations_with_icons
            .assign(tooltip_text=organizations_with_icons.name),
            get_icon='icon_data',
            get_size=4,
            size_scale=8,
            get_position=['x', 'y'],
            pickable=True,
        )
    )

if 'Actividad de organizaciones' in active_modes:
    layers.append(
        pdk.Layer(
            "HeatmapLayer",
            data=organization_agebs,
            get_position=['x', 'y'],
            opacity=0.7,
            intensity=1,
            radius_pixels=100,
            threshold=0.2,
            aggregation='MEAN',
            get_weight=1,
            weights_texture_size=512,
        )
    )
if 'Ganancias anuales' in active_modes:
    layers.append(
        pdk.Layer(
            "ScreenGridLayer",
            data=organizations
            .filter(items=['annual_income', 'lon', 'lat'])
            .dropna(subset=['lon', 'lat']),
            get_position=['lon', 'lat'],
            get_weight='1',
            cell_size_pixels=20,
            opacity=0.4,
        )
    )

if 'Año de incorporación legal' in active_modes:
    layers.append(
        pdk.Layer(
            "H3ClusterLayer",
            data=organizations
            .filter(['legal_incorporation_year', 'lon', 'lat']),
            get_position=['x', 'y'],
            pickable=True,
            stroked=True,
            filled=True,
            extruded=False,
            get_hexagons="hexIds",
            get_fill_color="[255, (1 - mean / 500) * 255, 0]",
            get_line_color=[246, 51, 102],
            line_width_min_pixels=2,
        )
    )

deck = pdk.Deck(
    layers,
    initial_view_state=pdk.ViewState(latitude=25.686613, longitude=-100.316116, zoom=10, max_zoom=16, min_zoom=10,
                                     pitch=30, bearing=-10),
    tooltip={
        'html': '{tooltip_text}',
    })
st.pydeck_chart(deck)
