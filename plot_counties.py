import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle

SELECTED_COLOR = "#fa26a0"


def plot_counties_by_connections_to_the_county(county_id, states, counties):

    county_name = counties.loc[county_id].NAME

    edge_color = "#30011E"
    background_color = "#fafafa"

    sns.set_style({
        "font.family": "serif",
        "figure.facecolor": background_color,
        "axes.facecolor": background_color
    })

    ax = counties.plot(edgecolor=edge_color + "55", color=counties.color, figsize=(20, 20))
    states.plot(ax=ax, edgecolor=edge_color, color="None", linewidth=1)

    add_titles(county_id, county_name)
    add_circle(ax, counties, county_id)

    plt.axis("off")
    plt.show()


def _add_centered_title(text, above_the_drawing, fontsize):
    plt.annotate(
        text=text,
        xy=(0.5, above_the_drawing), xycoords="axes fraction",
        fontsize=fontsize, ha="center"
    )


def add_titles(county_id, county_name):
    _add_centered_title(
        "Social Connectedness Ranking Between US Counties and",
        above_the_drawing=1.1, fontsize=16
    )
    _add_centered_title(
        f"{county_name} (FIPS Code {county_id})",
        above_the_drawing=1.03, fontsize=32
    )


def add_circle(ax, counties_df, county_id):
    center = counties_df[counties_df.index == county_id].geometry.centroid.iloc[0]
    ax.add_artist(
        Circle(
            radius=100000,
            xy=(center.x, center.y),
            facecolor="None",
            edgecolor=SELECTED_COLOR,
            linewidth=4
        )
    )
