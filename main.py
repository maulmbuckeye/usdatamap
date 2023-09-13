import numpy as np
import pandas as pd

import plot_counties as pc
import facebook_connections as fbc
import county as c
import usgeodata as usgd


def main():
    the_data = get_data(get_from_cache=True)
    do_repl_loop(the_data)


def get_data(get_from_cache: bool = True) \
        -> tuple[usgd.UsGeoData, usgd.UsGeoData, fbc.FacebookConnections]:
    counties = usgd.UsGeoData("./data/cb_2018_us_county_500k", get_from_cache)
    states = usgd.UsGeoData("./data/cb_2018_us_state_500k", get_from_cache)
    facebook = fbc.FacebookConnections()
    return counties, states, facebook


def do_repl_loop(the_data):
    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponse with 'exit' to exit; 'random' for random county.")
    while True:
        response = input("county_id: ").strip().lower()
        if response == "exit":
            break
        elif response == "random":
            random_fips = the_data[0].random_fips()
            try_to_plot_a_county(random_fips, the_data, data_breaks)
        else:
            try_to_plot_a_county(response, the_data, data_breaks)


def try_to_plot_a_county(candidate_county, the_data, p_data_breaks):
    counties, states, facebook = the_data
    try:
        the_county = c.County(candidate_county, counties.geodata)  # noqa
        counties.geodata = assign_color_to_counties_by_facebook_connections(
            counties, facebook, the_county)
        pc.plot_counties_by_connections_to_the_county(
            the_county, states, counties.geodata, p_data_breaks)
    except ValueError:
        print(f"\t[[{candidate_county}]] is a not a valid FIPS")


def assign_color_to_counties_by_facebook_connections(counties: usgd.UsGeoData,
                                                     facebook: fbc.FacebookConnections,
                                                     the_county: c.County) -> pd.DataFrame:
    counties.assign_values(facebook.get_number_of_connections_from_county(the_county.fips))
    counties.assign_colors(assign_color_based_on_percentile(counties, data_breaks))
    counties.assign_color_to_region(the_county.fips, pc.SELECTED_COLOR)

    return counties.geodata


data_breaks = [
    (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
    (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
    (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
    (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
    (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
]


def assign_color_based_on_percentile(usgd_counties: usgd.UsGeoData, p_data_breaks: list[tuple]) -> list[str]:
    colors: list[str] = []
    value_for_percentile = {
        percentile: np.percentile(usgd_counties.get_values(), percentile)
        for percentile, _, _ in p_data_breaks
    }
    counties = usgd_counties.geodata
    for _, county in counties.iterrows():
        for percentile, color, _ in p_data_breaks:
            if county.value >= value_for_percentile[percentile]:
                colors.append(color)
                break
    return colors


if __name__ == '__main__':
    main()
