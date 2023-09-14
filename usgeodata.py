from os.path import isfile
import geopandas as gpd
import pandas as pd
import geo_info as gi


class IndexErrorRegionNotFound(IndexError):
    def __init__(self, region: str = None, file: str = None):
        self.region = region
        self.file = file

    def __repr__(self):
        return f"IndexErrorRegionNotFound(region={self.region}, file={self.file})"


class UsGeoDataFactory:

    def __init__(self):
        self._path = ''
        self._path_to_gzip = ''
        self._geodata = None

    def get(self, path_to_data: str, try_cache: bool = True):
        self._path = path_to_data
        self._path_to_gzip = self._path + ".gzip"
        if try_cache and isfile(self._path_to_gzip):
            self._get_gzip_cache()
        else:
            self._produce_from_raw_data()
        if "county" in self._path:
            return UsCountiesData(self._geodata)
        return UsGeoData(self._geodata)

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

        self._geodata = UsGeoDataFactory._remove_states(geodata, gi.UNINCORPORATED_TERRORIES)

        # Change projection, i.e., Coordinate Reference Systems
        # https://geopandas.org/en/stable/docs/user_guide/projections.html
        self._geodata = self._geodata.to_crs("ESRI:102003")

        self._move_a_state(gi.ALASKA, 1300000, -4900000, 0.5, 32)
        self._move_a_state(gi.HAWAII, 5400000, -1500000, 1, 24)

        self._geodata.to_parquet(self._path_to_gzip)

    @classmethod
    def _remove_states(cls, gdf: gpd.GeoDataFrame,
                       states_to_exclude: list[str]) -> gpd.GeoDataFrame:
        return gdf[~gdf.STATEFP.isin(states_to_exclude)]

    @classmethod
    def _keep_states(cls, gdf: gpd.GeoDataFrame,
                     states_to_keep: list[str]) -> gpd.GeoDataFrame:
        return gdf[gdf.STATEFP.isin(states_to_keep)]

    def _move_a_state(self, a_state: str,
                      new_x, new_y, scale, rotate):
        geodata = self._geodata
        state_to_move: gpd.GeoDataFrame = UsGeoDataFactory._keep_states(geodata, [a_state])
        other_states: gpd.GeoDataFrame = UsGeoDataFactory._remove_states(geodata, [a_state])

        UsGeoDataFactory._update_geometry(state_to_move, new_x, new_y, scale, rotate)

        # No gpd.concat. Using pandas.concat instead, per
        # https://geopandas.org/en/stable/docs/user_guide/mergingdata.html.
        self._geodata = gpd.GeoDataFrame(pd.concat([other_states, state_to_move]))

    @staticmethod
    def _update_geometry(region: gpd.GeoDataFrame, x, y, scale, rotate):

        region.loc[:, "geometry"] = region.geometry.translate(xoff=x, yoff=y)
        center = region.dissolve().centroid.iloc[0]
        region.loc[:, "geometry"] = region.geometry.scale(xfact=scale, yfact=scale, origin=center)
        region.loc[:, "geometry"] = region.geometry.rotate(rotate, origin=center)


class UsGeoData:
    def __init__(self, geodata: gpd.GeoDataFrame):
        self._geodata = geodata

    def plot(self, *args, **kwargs):
        return self._geodata.plot(*args, **kwargs)

    def get_random_fips(self):
        random_county = self._geodata.sample(n=1)
        return random_county.index.values[0]

    def iter_all_counties(self):
        return self._geodata.iterrows()

    def get_name_of(self, fips: str) -> str:
        if not self.has_this_fips(fips):
            raise IndexErrorRegionNotFound(fips, __file__)
        return self._geodata.loc[fips].NAME

    def has_this_fips(self, fips):
        return fips in self._geodata.index

    def get_center_xy_of(self, fips: str) -> tuple[float, float]:
        if not self.has_this_fips(fips):
            raise IndexErrorRegionNotFound(fips, __file__)
        df = self._geodata
        centroid = df[df.index == fips].geometry.centroid.iloc[0]
        return centroid.x, centroid.y


class UsCountiesData(UsGeoData):
    def assign_values(self, values):
        self._geodata.loc[:, "value"] = values
        self._geodata.loc[:, "value"] = self._geodata["value"].fillna(0)

    def assign_colors(self, colors):
        self._geodata.loc[:, "color"] = colors

    def assign_color_to_region(self, fips, color):
        if not self.has_this_fips(fips):
            raise IndexErrorRegionNotFound(fips, __file__)
        self._geodata.loc[fips, "color"] = color

    @property
    def color(self):
        return self._geodata.color

    @property
    def value(self):
        return self._geodata.value
