import pandas as pd
import geo_info as gi
import geopandas as gpd
from os.path import isfile
import usgeodata as usgd

DEAULT_PATH_COUNTIES_DATA = "./data/cb_2018_us_county_500k"
DEFAULT_PATH_TO_STATES_DATA = "./data/cb_2018_us_state_500k"


class UsGeoDataFactory:
    def __init__(self):
        self._path = ''
        self._path_to_gzip = ''
        self._geodata = None

    def get(self, path_to_data: str, try_cache: bool = True)\
            -> usgd.UsCountiesData | usgd.UsGeoData:
        self._path = path_to_data
        self._path_to_gzip = self._path + ".gzip"
        if try_cache and isfile(self._path_to_gzip):
            self._get_gzip_cache()
        else:
            self._produce_from_raw_data()
        if "county" in self._path:
            return usgd.UsCountiesData(self._geodata)
        return usgd.UsGeoData(self._geodata)

    def _get_gzip_cache(self):
        print(f"Reading {self._path_to_gzip} ... ", end='')
        self._geodata = gpd.read_parquet(self._path_to_gzip)
        print("DONE")
        return

    def _produce_from_raw_data(self):
        print(f"Reading {self._path} ... ", end='')
        geodata = gpd.read_file(self._path)
        print("DONE")

        geodata.set_index("GEOID", inplace=True)

        self._geodata = _remove_states(geodata, gi.UNINCORPORATED_TERRORIES)

        self._drop_unneeded_columns(['AFFGEOID', 'ALAND', 'AWATER',
                                     'LSAD', 'COUNTYNS', 'STATENS'])

        # Change projection, i.e., Coordinate Reference Systems
        # https://geopandas.org/en/stable/docs/user_guide/projections.html
        self._geodata = self._geodata.to_crs("ESRI:102003")

        self._move_a_state(gi.ALASKA, 1300000, -4900000, 0.5, 32)
        self._move_a_state(gi.HAWAII, 5400000, -1500000, 1, 24)

        self._geodata.to_parquet(self._path_to_gzip)

    def _drop_unneeded_columns(self, possible_columns_to_drop):
        columns_to_drop = [
            col
            for col in possible_columns_to_drop
            if col in self._geodata.columns
        ]
        # Trying the drop in place caused this warning:
        # A value is trying to be set on a copy of a slice from a DataFrame
        # See the caveats in the documentation:
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
        self._geodedata = self._geodata.drop(columns=columns_to_drop)

    def _move_a_state(self, a_state: str,
                      new_x, new_y, scale, rotate):
        geodata = self._geodata
        state_to_move: gpd.GeoDataFrame = _keep_states(geodata, [a_state])
        other_states: gpd.GeoDataFrame = _remove_states(geodata, [a_state])

        _update_geometry(state_to_move, new_x, new_y, scale, rotate)

        # No gpd.concat. Using pandas.concat instead, per
        # https://geopandas.org/en/stable/docs/user_guide/mergingdata.html.
        self._geodata = gpd.GeoDataFrame(pd.concat([other_states, state_to_move]))


def _update_geometry(region: gpd.GeoDataFrame, x, y, scale, rotate):
    region.loc[:, "geometry"] = region.geometry.translate(xoff=x, yoff=y)
    center = region.dissolve().centroid.iloc[0]
    region.loc[:, "geometry"] = region.geometry.scale(xfact=scale, yfact=scale, origin=center)
    region.loc[:, "geometry"] = region.geometry.rotate(rotate, origin=center)


def _remove_states(gdf: gpd.GeoDataFrame,
                   states_to_exclude: list[str]) -> gpd.GeoDataFrame:
    return gdf[~gdf.STATEFP.isin(states_to_exclude)]


def _keep_states(gdf: gpd.GeoDataFrame,
                 states_to_keep: list[str]) -> gpd.GeoDataFrame:
    return gdf[gdf.STATEFP.isin(states_to_keep)]
