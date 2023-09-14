import usgeodata as usgd


class County:
    def __init__(self, fips: str, usgd_counties: usgd.UsGeoData):
        self.__fips = fips
        self.__name = usgd_counties.get_name_of(self.__fips)
        self.__center_xy = usgd_counties.get_center_xy_of(self.__fips)

    @property
    def fips(self):
        return self.__fips

    @property
    def name(self):
        return self.__name

    @property
    def center_xy(self):
        return self.__center_xy
