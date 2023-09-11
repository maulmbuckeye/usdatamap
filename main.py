import numpy as np
import pandas as pd
import geopandas as gpd
from os.path import isfile

from PIL import Image


import geo_info as gi
import plot_counties as pc


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


def create_color(county_df: pd.DataFrame, data_breaks: list[tuple]) -> list[str]:
    colors = []
    lookup = {p: np.percentile(county_df.value, p) for p, _, _ in data_breaks}
    for _, county in county_df.iterrows():
        for p, c, _ in data_breaks:
            if county.value >= lookup[p]:
                colors.append(c)
                break
    return colors


def assign_color_to_counties_by_facebook_connections(counties, facebook_df, county_id):
    county_facebook_df = facebook_df.df[facebook_df.df.user_loc == county_id]

    data_breaks = [
        (90, "#00ffff", "Top 10%"),
        (70, "#00b5ff", "90-70%"),
        (50, "#6784ff", "70-50%"),
        (30, "#aeb3fe", "50-30%"),
        (0, "#e6e5fc", "Bottom 30%")
    ]

    counties.loc[:, "value"] = county_facebook_df.set_index("fr_loc").scaled_sci
    counties.loc[:, "value"] = counties["value"].fillna(0)
    counties.loc[:, "color"] = create_color(counties, data_breaks)
    counties.loc[county_id, "color"] = pc.SELECTED_COLOR

    return counties


def main():
    counties = get_us_geo_data("./data/cb_2018_us_county_500k")
    counties = counties.set_index("GEOID")

    states = get_us_geo_data("./data/cb_2018_us_state_500k")

    facebook_df = FacebookData()
    facebook_df.get()

    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponse with 'exit' to exit")
    while True:
        county_id = input("county_id=").strip()
        if county_id.lower() == "exit":
            break
        counties = assign_color_to_counties_by_facebook_connections(counties, facebook_df, county_id)
        pc.plot_counties_by_connections_to_the_county(county_id, states, counties)


class FacebookData:
    FACEBOOK_DATA_GZIP = "./data/county_county.gzip"
    FACEBOOK_DATA_TSV = "./data/county_county.tsv"

    def __init__(self):
        pass

    def get(self):
        if isfile(self.FACEBOOK_DATA_GZIP):
            print(f"Reading {self.FACEBOOK_DATA_GZIP} ... ", end='')
            self.df = pd.read_parquet(self.FACEBOOK_DATA_GZIP)  # noqa
            print("DONE")
        else:
            self._get_from_tsv()

    def _get_from_tsv(self):
        print(f"Reading {self.FACEBOOK_DATA_TSV} ... ", end='')
        df = pd.read_csv(self.FACEBOOK_DATA_TSV, sep="\t")     # noqa
        print("DONE")

        df.user_loc = ("0" + df.user_loc.astype(str)).str[-5:]
        df.fr_loc = ("0" + df.fr_loc.astype(str)).str[-5:]
        df.to_parquet(self.FACEBOOK_DATA_GZIP, compression="gzip")
        self.df = df


if __name__ == '__main__':
    main()
