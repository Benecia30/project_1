import pandas as pd
import geopandas as gpd
import core.HelperTools as ht

import folium
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import streamlit as st

# -----------------------------------------------------------------------------


def sort_by_plz_add_geometry(dfr, dfg, pdict): 
    """
    Sorts DataFrame by PLZ and merges it with GeoDataFrame to add geometry.
    """
    dframe = dfr.copy()
    df_geo = dfg.copy()
    
    sorted_df = (
        dframe.sort_values(by='PLZ')
              .reset_index(drop=True)
              .sort_index()
    )
        
    sorted_df2 = sorted_df.merge(df_geo, on=pdict["geocode"], how='left')
    sorted_df3 = sorted_df2.dropna(subset=['geometry'])
    
    sorted_df3['geometry'] = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    ret = gpd.GeoDataFrame(sorted_df3, geometry='geometry')
    
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """
    Preprocesses the Ladesaeulenregister.csv file.
    Filters data, processes columns, and adds geometry for Berlin-specific PLZs.
    """
    dframe = dfr.copy()
    df_geo = dfg.copy()
    
    dframe2 = dframe.loc[:, ['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"}, inplace=True)

    # Correct data formatting
    for col in ['Breitengrad', 'Längengrad']:
        dframe2[col] = dframe2[col].astype(str).str.replace(',', '.')

    # Filter Berlin-specific PLZ
    dframe3 = dframe2[
        (dframe2["Bundesland"] == 'Berlin') & 
        (dframe2["PLZ"] > 10115) & 
        (dframe2["PLZ"] < 14200)
    ]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def count_plz_occurrences(df_lstat2):
    """
    Counts occurrences of loading stations by PLZ.
    """
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    return result_df


# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """
    Preprocesses the plz_einwohner.csv file.
    Filters data, processes columns, and adds geometry for Berlin-specific PLZs.
    """
    dframe = dfr.copy()
    df_geo = dfg.copy()    
    
    dframe2 = dframe.loc[:, ['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns={"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace=True)

    # Correct data formatting
    for col in ['Breitengrad', 'Längengrad']:
        dframe2[col] = dframe2[col].astype(str).str.replace(',', '.')

    # Filter Berlin-specific PLZ
    dframe3 = dframe2[
        (dframe2["PLZ"] > 10000) & 
        (dframe2["PLZ"] < 14200)
    ]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """
    Creates a Streamlit app with heatmaps of electric charging stations and residents.
    """
    dframe1 = dfr1.copy()
    dframe2 = dfr2.copy()

    # Streamlit setup
    st.title('Heatmaps: Electric Charging Stations and Residents')
    layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations"))

    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        # Residents heatmap
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe2['Einwohner'].min(), vmax=dframe2['Einwohner'].max())
        for _, row in dframe2.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Einwohner']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
            ).add_to(m)
    else:
        # Charging stations heatmap
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe1['Number'].min(), vmax=dframe1['Number'].max())
        for _, row in dframe1.iterrows():
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color_map(row['Number']): {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                },
                tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}"
            ).add_to(m)

    # Add color map and display
    color_map.add_to(m)
    folium_static(m, width=800, height=600)
