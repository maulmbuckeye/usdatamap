import numpy as np

import county as cty
import facebook_connections as fbc
import plot_counties as pc
import usgeodata as usgd
import usgeodatafactory as ugfac


class GeoConnections:
    def __init__(self, try_cache=True):
        self.counties = None
        self.states = None
        self.facebook = None
        self.get_data(try_cache)
        self.fac = ugfac.UsGeoDataFactory()

    @property
    def values(self):
        return self.counties, self.states, self.facebook

    def get_random_county(self):
        return self.counties.get_random_fips()

    def get_data(self, try_cache: bool = True):
        self.states = self.fac.get("./data/cb_2018_us_state_500k", try_cache)
        self.counties = self.fac.get("./data/cb_2018_us_county_500k", try_cache)
        self.facebook = fbc.FacebookConnections()

    def plot_a_county(self, candidate_county, p_data_breaks):
        try:
            the_county = cty.County(candidate_county, self.counties)
        except usgd.IndexErrorRegionNotFound:
            print(f"\t[[{candidate_county}]] is a not a valid FIPS")
            return

        self.counties = assign_color_to_counties_by_facebook_connections(
            self.counties,
            self.facebook,
            the_county)
        pc.plot_counties_by_connections_to_the_county(
            the_county,
            self.states,
            self.counties,
            p_data_breaks)


def main():
    geo_connect = GeoConnections(try_cache=True)
    do_repl_loop(geo_connect)


def do_repl_loop(geo_connect):
    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponsd with 'exit' to exit; 'random' for random county; 'refresh' to get uncached data")
    while True:
        response = input("county_id: ").strip().lower()
        if response == "exit":
            break
        elif response == "random":
            random_fips = geo_connect.get_random_county()
            geo_connect.plot_a_county(random_fips, data_breaks)
        elif response == "refresh":
            geo_connect.get_data(try_cache=False)
        else:
            geo_connect.plot_a_county(response, data_breaks)


def assign_color_to_counties_by_facebook_connections(
        counties: usgd.UsCountiesData,
        facebook: fbc.FacebookConnections,
        the_county: cty.County) -> usgd.UsGeoData:

    counties.assign_values(facebook.get_number_of_connections_from_county(the_county.fips))
    counties.assign_colors(select_color_based_on_percentile(counties, data_breaks))
    counties.assign_color_to_region(the_county.fips, pc.SELECTED_COLOR)

    return counties


data_breaks = [
    (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
    (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
    (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
    (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
    (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
]


def select_color_based_on_percentile(
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


if __name__ == '__main__':
    main()
