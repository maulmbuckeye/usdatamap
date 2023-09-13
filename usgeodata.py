from os.path import isfile
import geopandas as gpd
import pandas as pd
import geo_info as gi


class UsGeoData:
    def __init__(self, path_to_data: str, get_from_cache: bool = True):
        self._path = path_to_data
        self._path_to_gzip = self._path + ".gzip"
        self._geodata = gpd.GeoDataFrame()
        self._get(get_from_cache)

    def plot(self, *args, **kwargs):
        return self._geodata.plot(*args, **kwargs)

    def get_random_fips(self):
        random_county = self._geodata.sample(n=1)
        return random_county.index.values[0]

    @property
    def value(self):
        return self._geodata.value

    @property
    def color(self):
        return self._geodata.color

    def iter_all_counties(self):
        return self._geodata.iterrows()

    def get_name_of(self, fips: str) -> str:
        if not self.has_this_fips(fips):
            raise ValueError
        return self._geodata.loc[fips].NAME

    def has_this_fips(self, fips):
        return fips in self._geodata.index

    def get_centroid_of(self, fips: str):
        if not self.has_this_fips(fips):
            raise ValueError
        df = self._geodata
        return df[df.index == fips].geometry.centroid.iloc[0]

    # Assignment are all part coloring which chould be pushed down.

    def assign_values(self, values):
        self._geodata.loc[:, "value"] = values
        self._geodata.loc[:, "value"] = self._geodata["value"].fillna(0)

    def assign_colors(self, colors):
        self._geodata.loc[:, "color"] = colors

    def assign_color_to_region(self, fips, color):
        if not self.has_this_fips(fips):
            raise ValueError
        self._geodata.loc[fips, "color"] = color

    # Getting data. This should be moved out of here

    def _get(self, get_from_cache: bool = True):
        if get_from_cache and isfile(self._path_to_gzip):
            self._geodata = self._get_gzip_cache()
        else:
            self._geodata = self._produce_from_raw_data()

    def _get_gzip_cache(self):
        print(f"Reading {self._path_to_gzip} ... ", end='')
        geodata = gpd.read_parquet(self._path_to_gzip)
        print("DONE")
        return geodata

    def _produce_from_raw_data(self):
        print(f"Reading {self._path} ... ", end='')
        self._geodata = gpd.read_file(self._path)
        print("DONE")
        self._geodata = self._geodata.set_index("GEOID")

        self._geodata = self._geodata[~self._geodata.STATEFP.isin(gi.UNINCORPORATED_TERRORIES)]

        # Change projection, i.e., Coordinate Reference Systems
        # https://geopandas.org/en/stable/docs/user_guide/projections.html
        self._geodata = self._geodata.to_crs("ESRI:102003")

        self._geodata = self._move_a_state(gi.ALASKA, 1300000, -4900000, 0.5, 32)
        self._geodata = self._move_a_state(gi.HAWAII, 5400000, -1500000, 1, 24)

        self._geodata.to_parquet(self._path_to_gzip)

        return self._geodata

    def _move_a_state(self, state_to_move: str,
                      new_x, new_y, scale, rotate) -> gpd.GeoDataFrame:  # noqa
        df_state_to_move = self._geodata[self._geodata.STATEFP == state_to_move]
        df_other_states = self._geodata[~self._geodata.STATEFP.isin([state_to_move])]

        df_state_to_move = self._translate_geometries(df_state_to_move, new_x, new_y, scale, rotate)

        # Does not appear to be gpd.concat.
        return gpd.GeoDataFrame(pd.concat([df_other_states, df_state_to_move]))

    def _translate_geometries(self, df, x, y, scale, rotate):  # noqa
        df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
        center = df.dissolve().centroid.iloc[0]
        df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
        df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)

        return df
