# currentWorkingDirectory = "C:\\(...)\\project1"
# currentWorkingDirectory = "D:\BHT-university\advanced software engineering-Fortgeschrittene Softwaretechnik\project\berlingeoheatmap_project1"
currentWorkingDirectory = "C:/Users/dsouz/OneDrive/Desktop/project_1"

# -----------------------------------------------------------------------------
import os
os.chdir(currentWorkingDirectory)
print("Current working directory\n" + os.getcwd())

import pandas as pd
from core import methods  as m1
from core import HelperTools as ht
from config import pdict
import geopandas as gpd
# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""
   # Load datasets
   # plz_geo_file = "D:/BHT-university/advanced software engineering-Fortgeschrittene Softwaretechnik/project/plz_geo.json"
    plz_geo_file = "C:/Users/dsouz/OneDrive/Desktop/project_1/datasets/geodata_berlin_plz.csv"
    ladesaeulen_file = "C:/Users/dsouz/OneDrive/Desktop/project_1/datasets/Ladesaeulenregister.csv"
    residents_file = "C:/Users/dsouz/OneDrive/Desktop/project_1/datasets/plz_einwohner.csv"

    # Reading GeoDataFrame for PLZ geometries
    # df_geodat_plz = gpd.read_file(plz_geo_file)
    df_geodat_plz = pd.read_csv(plz_geo_file, sep=';', encoding='utf-8')


    # Reading electric charging stations data
    df_lstat = pd.read_csv(ladesaeulen_file, sep=';', skiprows=10, encoding='utf-8', low_memory=False)
 
    # Reading residents data
    df_residents = pd.read_csv(residents_file, sep=',', encoding='utf-8')

    # Preprocessing electric charging stations
    df_lstat2 = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = m1.count_plz_occurrences(df_lstat2)

    # Preprocessing residents data
    gdf_residents2 = m1.preprop_resid(df_residents, df_geodat_plz, pdict)

# Generate Streamlit app with heatmaps
    m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)


# -----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__": 
    main()