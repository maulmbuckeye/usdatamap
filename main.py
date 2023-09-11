import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from os.path import isfile

from PIL import Image
from matplotlib.patches import Patch, Circle

# FIPS codes per state https://www.census.gov/library/reference/code-lists/ansi/ansi-codes-for-states.html
UNINCORPORATED_TERRORIES = ["72", "69", "60", "66", "78"]
ALASKA = "02"
CALIFORNIA = "06"
HAWAII = "15"
OHIO = "39"


def get_us_geo_data(path_to_data: str):
    print(f"Reading {path_to_data} ... ", end='')
    geodata = gpd.read_file(path_to_data)
    print("DONE")

    geodata = geodata[~geodata.STATEFP.isin(UNINCORPORATED_TERRORIES)]

    # Change projection, i.e., Coordinate Reference Systems
    # https://geopandas.org/en/stable/docs/user_guide/projections.html
    geodata = geodata.to_crs("ESRI:102003")

    geodata = move_a_state(geodata, ALASKA, 1300000, -4900000, 0.5, 32)
    geodata = move_a_state(geodata, HAWAII, 5400000, -1500000, 1, 24)

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
    for _, row in county_df.iterrows():
        for p, c, _ in data_breaks:
            if row.value >= np.percentile(county_df.value, p):
                colors.append(c)
                break
    return colors


def main():
    edge_color = "#30011E"
    background_color = "#fafafa"

    sns.set_style({
        "font.family": "serif",
        "figure.facecolor": background_color,
        "axes.facecolor": background_color
    })

    # https://www.census.gov/library/reference/code-lists/ansi.html#cou
    # GOID is six right most digts of the COUNTYNS
    counties = get_us_geo_data("./data/cb_2018_us_county_500k")
    counties = counties.set_index("GEOID")

    states = get_us_geo_data("./data/cb_2018_us_state_500k")

    facebook_df = FacebookData()
    facebook_df.get()
    print(facebook_df.df.head(5))
    SAN_FRANCISCO_CA_COUNTY = "06075"
    WARREN_OH_COUNTY = "39165"
    county_id = WARREN_OH_COUNTY

    county_facebook_df = facebook_df.df[facebook_df.df.user_loc == county_id]

    selected_color = "#fa26a0"
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
    counties.loc[county_id, "color"] = selected_color

    county_name = counties.loc[county_id].NAME

    ax = counties.plot(edgecolor=edge_color + "55", color=counties.color, figsize=(20, 20))
    states.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)

    plt.axis("off")
    plt.show()


class FacebookData():
    FACEBOOK_DATA = "./data/county_county.gzip"

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
