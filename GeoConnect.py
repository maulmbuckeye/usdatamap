import county as cty
import facebook_connections as fbc
import usgeodatafactory as ugfac
import usgeodata as usgd
import plot_counties as pc
import numpy as np


class GeoConnections:
    def __init__(self, try_cache=True):
        self.fac = ugfac.UsGeoDataFactory()
        self.counties = None
        self.states = None
        self.facebook = None
        self.get_data(try_cache)
        self.data_breaks = [
            (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
            (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
            (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
            (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
            (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
        ]

    def get_random_county(self):
        return self.counties.get_random_fips()

    def get_data(self, try_cache: bool = True):
        self.states = self.fac.get("./data/cb_2018_us_state_500k", try_cache)
        self.counties = self.fac.get("./data/cb_2018_us_county_500k", try_cache)
        self.facebook = fbc.FacebookConnections()

    def plot_a_county(self, candidate_county):
        try:
            the_county = cty.County(candidate_county, self.counties)
        except usgd.IndexErrorRegionNotFound:
            print(f"\t[[{candidate_county}]] is a not a valid FIPS")
            return

        self._update_county_color_using_fb_connections(the_county)
        pc.plot_counties_by_connections_to_the_county(
            the_county,
            self.states,
            self.counties,
            self.data_breaks)

    def _update_county_color_using_fb_connections(self, the_county: cty.County):
        counties = self.counties
        facebook = self.facebook
        counties.assign_values(facebook.get_number_of_connections_from_county(the_county.fips))
        counties.assign_colors(_select_color_based_on_percentile(counties, self.data_breaks))
        counties.assign_color_to_region(the_county.fips, pc.SELECTED_COLOR)

        self.counties = counties


def _select_color_based_on_percentile(
        counties: usgd.UsCountiesData,
        p_data_breaks: list[tuple]) -> list[str]:

    value_for_percentile = {
        percentile: np.percentile(counties.value, percentile)
        for percentile, _, _ in p_data_breaks
    }

    colors: list[str] = []
    for _, county in counties.iter_all_counties():
        for percentile, color, _ in p_data_breaks:
            if county.value >= value_for_percentile[percentile]:
                colors.append(color)
                break
    return colors
