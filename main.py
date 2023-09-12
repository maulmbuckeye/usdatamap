import numpy as np
import pandas as pd
import geopandas as gpd
from os.path import isfile

import geo_info as gi
import plot_counties as pc
import facebook_connections as fbc

data_breaks = [
    (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
    (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
    (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
    (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
    (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
]


def translate_geometries(df, x, y, scale, rotate):        # noqa
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)

    return df


def move_a_state(df, state_to_move: str, new_x, new_y, scale, rotate): # noqa
    df_state_to_move = df[df.STATEFP == state_to_move]
    df_other_states = df[~df.STATEFP.isin([state_to_move])]

    df_state_to_move = translate_geometries(df_state_to_move, new_x, new_y, scale, rotate)

    return pd.concat([df_other_states, df_state_to_move])


def get_us_geo_data(path_to_data: str):

    path_to_gzip = path_to_data + ".gzip"
    if isfile(path_to_gzip):
        print(f"Reading {path_to_gzip} ... ", end='')
        geodata = gpd.read_parquet(path_to_gzip)
        print("DONE")
        return geodata

    print(f"Reading {path_to_data} ... ", end='')
    geodata = gpd.read_file(path_to_data)
    print("DONE")

    geodata = geodata[~geodata.STATEFP.isin(gi.UNINCORPORATED_TERRORIES)]

    # Change projection, i.e., Coordinate Reference Systems
    # https://geopandas.org/en/stable/docs/user_guide/projections.html
    geodata = geodata.to_crs("ESRI:102003")

    geodata = move_a_state(geodata, gi.ALASKA, 1300000, -4900000, 0.5, 32)
    geodata = move_a_state(geodata, gi.HAWAII, 5400000, -1500000, 1, 24)

    geodata.to_parquet(path_to_gzip)

    return geodata


def assign_color_based_on_percentile(county_df: pd.DataFrame, data_breaks: list[tuple]) -> list[str]:
    colors = []
    lookup = {p: np.percentile(county_df.value, p) for p, _, _ in data_breaks}
    for _, county in county_df.iterrows():
        for p, c, _ in data_breaks:
            if county.value >= lookup[p]:
                colors.append(c)
                break
    return colors


def assign_color_to_counties_by_facebook_connections(counties,
                                                     facebook,
                                                     county):

    counties.loc[:, "value"] = facebook.get_number_of_connections_from_county(county.fips)
    counties.loc[:, "value"] = counties["value"].fillna(0)
    counties.loc[:, "color"] = assign_color_based_on_percentile(counties, data_breaks)
    counties.loc[county.fips, "color"] = pc.SELECTED_COLOR

    return counties


def main():
    counties = get_us_geo_data("./data/cb_2018_us_county_500k")
    counties = counties.set_index("GEOID")

    states = get_us_geo_data("./data/cb_2018_us_state_500k")

    facebook = fbc.FacebookConnections()
    facebook.get()

    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponse with 'exit' to exit")
    while True:
        response = input("county_id: ").strip()
        if response.lower() == "exit":
            break
        county = County(response, counties)
        counties = assign_color_to_counties_by_facebook_connections(counties, facebook, county)
        pc.plot_counties_by_connections_to_the_county(county, states, counties, data_breaks)


class County:

    def __init__(self, fips: str, counties: gpd.GeoDataFrame):
        self.fips = fips
        self.center = counties[counties.index == self.fips].geometry.centroid.iloc[0]
        self.name = counties.loc[self.fips].NAME


if __name__ == '__main__':
    main()
