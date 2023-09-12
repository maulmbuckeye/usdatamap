import geopandas as gpd


class County:
    def __init__(self, fips: str, counties: gpd.GeoDataFrame):
        self.fips = fips
        if self.fips not in counties.index:
            raise ValueError
        self.center = counties[counties.index == self.fips].geometry.centroid.iloc[0]
        self.name = counties.loc[self.fips].NAME
