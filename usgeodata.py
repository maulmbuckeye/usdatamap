import geopandas as gpd
import pandas as pd


class IndexErrorRegionNotFound(IndexError):
    def __init__(self, region: str = None, file: str = None):
        self.region = region
        self.file = file

    def __repr__(self):
        return f"IndexErrorRegionNotFound(region={self.region}, file={self.file})"


class UsGeoData:
    def __init__(self, geodata: gpd.GeoDataFrame):
        self._geodata = geodata

    def plot(self, *args, **kwargs):
        return self._geodata.plot(*args, **kwargs)

    def get_random_fips(self):
        random_county = self._geodata.sample(n=1)
        return random_county.index.values[0]

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
    def color(self) -> pd.Series:
        return self._geodata.color

    @property
    def value(self) -> pd.Series:
        return self._geodata.value
