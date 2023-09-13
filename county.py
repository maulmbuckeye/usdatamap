import usgeodata as usgd


class County:
    def __init__(self, fips: str, usgd_counties: usgd.UsGeoData):
        self._fips = fips
        self._name = usgd_counties.get_name_of(self._fips)
        self._centroid = usgd_counties.get_centroid_of(self._fips)

    @property
    def fips(self):
        return self._fips

    @property
    def name(self):
        return self._name

    @property
    def centriod(self):
        return self._centroid
