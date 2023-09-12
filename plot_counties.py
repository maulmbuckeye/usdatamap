import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle

SELECTED_COLOR = "#fa26a0"
EDGE_COLOR = "#30011E"
BACKGROUND_COLOR = "#fafafa"


def plot_counties_by_connections_to_the_county(county_id, states, counties, data_breaks):

    county_name = counties.loc[county_id].NAME

    sns.set_style({
        "font.family": "serif",
        "figure.facecolor": BACKGROUND_COLOR,
        "axes.facecolor": BACKGROUND_COLOR
    })

    ax = counties.plot(edgecolor=EDGE_COLOR + "55", color=counties.color, figsize=(20, 20))
    states.plot(ax=ax, edgecolor=EDGE_COLOR, color="None", linewidth=1)

    add_titles(county_id, county_name)
    add_circle(ax, counties, county_id)
    add_legend(data_breaks, county_name)
    add_information()

    plt.axis("off")
    plt.show()


def _add_centered_title(text, above_the_drawing, fontsize, *, linespacing=1.0, va="bottom"):
    plt.annotate(
        text=text,
        xy=(0.5, above_the_drawing),
        xycoords="axes fraction", ha="center", va=va,
        fontsize=fontsize, linespacing=linespacing
    )


def add_information():

    explain = """The Facebook Connectivity Index measures the likelyhood that user in different
    locations are connected on Facebook. The formula divides the number of Facebook
    connections with the number of possible connections for the two locations."""
    _add_centered_title(explain, above_the_drawing=-0.0, fontsize=14,
                        linespacing=1.4, va="top")
    _add_centered_title('Source: https://dataforgood.facebook.com', above_the_drawing=-0.14, fontsize=12)


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


def add_legend(data_breaks, county_name):
    data_breaks = [Patch(facecolor=c, edgecolor=EDGE_COLOR, label=text)
                   for _, c, text in data_breaks]
    selected_county = [Patch(facecolor=SELECTED_COLOR, edgecolor=EDGE_COLOR, label=county_name)]
    patches = selected_county + data_breaks

    _ = plt.legend(
        handles=patches
    )
