import numpy as np
import pandas as pd

import plot_counties as pc
import facebook_connections as fbc
import county as c
import usgeodata as usgd


def main():
    counties = usgd.UsGeoData("./data/cb_2018_us_county_500k")
    states = usgd.UsGeoData("./data/cb_2018_us_state_500k")
    facebook = fbc.FacebookConnections()

    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponse with 'exit' to exit")
    while True:
        response = input("county_id: ").strip()
        if response.lower() == "exit":
            break
        try:
            the_county = c.County(response, counties.geodata) # noqa
            counties.geodata = assign_color_to_counties_by_facebook_connections(
                counties, facebook, the_county)
            pc.plot_counties_by_connections_to_the_county(
                the_county, states, counties.geodata, data_breaks)
        except ValueError:
            print(f"\t[[{response}]] is a not a valid FIPS")


def assign_color_to_counties_by_facebook_connections(counties: usgd.UsGeoData,
                                                     facebook: fbc.FacebookConnections,
                                                     the_county: c.County) -> pd.DataFrame:
    counties.assign_values(facebook.get_number_of_connections_from_county(the_county.fips))
    counties.assign_colors(assign_color_based_on_percentile(counties.geodata, data_breaks))
    counties.assign_color_to_region(the_county.fips, pc.SELECTED_COLOR)

    return counties.geodata


data_breaks = [
    (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
    (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
    (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
    (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
    (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
]


def assign_color_based_on_percentile(counties: pd.DataFrame, p_data_breaks: list[tuple]) -> list[str]:
    colors: list[str] = []
    value_for_percentile = {percentile: np.percentile(counties.value, percentile)
                            for percentile, _, _ in p_data_breaks}
    for _, county in counties.iterrows():
        for percentile, color, _ in p_data_breaks:
            if county.value >= value_for_percentile[percentile]:
                colors.append(color)
                break
    return colors


if __name__ == '__main__':
    main()
