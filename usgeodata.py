from os.path import isfile
import geopandas as gpd
import pandas as pd
import geo_info as gi


class UsGeoData:
    def __init__(self, path_to_data: str, get_from_cache: bool = True):
        self._path = path_to_data
        self._path_to_gzip = self._path + ".gzip"
        self.geodata = gpd.GeoDataFrame()
        self._get(get_from_cache)

    def _get(self, get_from_cache: bool = True):
        if get_from_cache and isfile(self._path_to_gzip):
            self.geodata = self._get_gzip_cache()
        else:
            self.geodata = self._produce_from_raw_data()

    def plot(self, *args, **kwargs):
        self.geodata.plot(*args, **kwargs)

    def assign_values(self, values):
        self.geodata.loc[:, "value"] = values
        self.geodata.loc[:, "value"] = self.geodata["value"].fillna(0)

    def assign_colors(self, colors):
        self.geodata.loc[:, "color"] = colors

    def random_fips(self):
        random_county = self.geodata.sample(n=1)
        return random_county.index.values[0]

    def get_values(self):
        return self.geodata.value

    def iter_all_counties(self):
        return self.geodata.iterrows()

    def assign_color_to_region(self, fips, color):
        self.geodata.loc[fips, "color"] = color

    def _get_gzip_cache(self):
        print(f"Reading {self._path_to_gzip} ... ", end='')
        geodata = gpd.read_parquet(self._path_to_gzip)
        print("DONE")
        return geodata

    def _produce_from_raw_data(self):
        print(f"Reading {self._path} ... ", end='')
        self.geodata = gpd.read_file(self._path)
        print("DONE")
        self.geodata = self.geodata.set_index("GEOID")

        self.geodata = self.geodata[~self.geodata.STATEFP.isin(gi.UNINCORPORATED_TERRORIES)]

        # Change projection, i.e., Coordinate Reference Systems
        # https://geopandas.org/en/stable/docs/user_guide/projections.html
        self.geodata = self.geodata.to_crs("ESRI:102003")

        self.geodata = self._move_a_state(gi.ALASKA, 1300000, -4900000, 0.5, 32)
        self.geodata = self._move_a_state(gi.HAWAII, 5400000, -1500000, 1, 24)

        self.geodata.to_parquet(self._path_to_gzip)

        return self.geodata

    def _move_a_state(self, state_to_move: str,
                      new_x, new_y, scale, rotate) -> gpd.GeoDataFrame:  # noqa
        df_state_to_move = self.geodata[self.geodata.STATEFP == state_to_move]
        df_other_states = self.geodata[~self.geodata.STATEFP.isin([state_to_move])]

        df_state_to_move = self._translate_geometries(df_state_to_move, new_x, new_y, scale, rotate)

        # Does not appear to be gpd.concat.
        return gpd.GeoDataFrame(pd.concat([df_other_states, df_state_to_move]))

    def _translate_geometries(self, df, x, y, scale, rotate):  # noqa
        df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
        center = df.dissolve().centroid.iloc[0]
        df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
        df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)

        return df
