import usgeodata as usgd


class County:
    def __init__(self, fips: str, usgd_counties: usgd.UsGeoData):
        self._fips = fips
        self._name = usgd_counties.get_name_of(self._fips)
        self._center_xy = usgd_counties.get_center_xy_of(self._fips)

    @property
    def fips(self):
        return self._fips

    @property
    def name(self):
        return self._name

    @property
    def center_xy(self):
        return self._center_xy
