import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.patches import Patch, Circle

UNINCORPORATED_TERRORIES = ["72", "69", "60", "66", "78"]


def get_us_geo_data(path_to_data: str):
    print(f"Reading county info {path_to_data} ... ", end='')
    geodata = gpd.read_file(path_to_data)
    print("DONE")

    geodata = geodata[~geodata.STATEFP.isin(UNINCORPORATED_TERRORIES)]

    # Change projection, i.e., Coordinate Reference Systems
    # https://geopandas.org/en/stable/docs/user_guide/projections.html
    geodata = geodata.to_crs("ESRI:102003")

    geodata = adjust_maps(geodata)

    return geodata


def translate_geometries(df, x, y, scale, rotate):
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)

    return df


def adjust_maps(df):
    df_main_land = df[~df.STATEFP.isin(["02", "15"])]
    df_alaska = df[df.STATEFP == "02"]
    df_hawaii = df[df.STATEFP == "15"]

    df_alaska = translate_geometries(df_alaska, 1300000, -4900000, 0.5, 32)
    df_hawaii = translate_geometries(df_hawaii, 5400000, -1500000, 1, 24)

    return pd.concat([df_main_land, df_alaska, df_hawaii])


def main():
    edge_color = "#30011E"
    background_color = "#fafafa"

    sns.set_style({
        "font.family": "serif",
        "figure.facecolor": background_color,
        "axes.facecolor": background_color
    })

    counties = get_us_geo_data("./data/cb_2018_us_county_500k")
    counties = counties.set_index("GEOID")

    states = get_us_geo_data("./data/cb_2018_us_state_500k")

    ax = counties.plot(edgecolor=edge_color + "55", color="None", figsize=(20, 20))
    states.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)

    plt.axis("off")
    plt.show()


if __name__ == '__main__':
    main()
