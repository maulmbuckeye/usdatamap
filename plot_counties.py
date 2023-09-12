import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle

SELECTED_COLOR = "#fa26a0"    # #fa26a0  a magneta
EDGE_COLOR = "#30011E"        # #30011e  a dark black
BACKGROUND_COLOR = "#fafafa"  # #fafa#fa Gray98, an almost white grey
DISPLAY_GRADIENT_1 = "#00ffff"
DISPLAY_GRADIENT_2 = "#00b5ff"
DISPLAY_GRADIENT_3 = "#6784ff"
DISPLAY_GRADIENT_4 = "#aeb3fe"
DISPLAY_GRADIENT_5 = "#e6e5fc"

FIG_SIZE_FOR_MY_LARGE_SCREEN = 14, 9


def make_transparent(color):
    return color + "55"


def plot_counties_by_connections_to_the_county(county, states, counties, data_breaks):

    sns.set_style({
        "font.family": "serif",
        "figure.facecolor": BACKGROUND_COLOR,
        "axes.facecolor": BACKGROUND_COLOR
    })

    ax = counties.plot(edgecolor=make_transparent(EDGE_COLOR),
                       color=counties.color,
                       figsize=FIG_SIZE_FOR_MY_LARGE_SCREEN)
    states.plot(ax=ax, edgecolor=EDGE_COLOR,
                color="None", linewidth=1)
    ax.set(xlim=(-2600000, None))  # Remove some of the padding to the left of diagram

    add_titles(county)
    add_circle(ax, county)
    add_legend(data_breaks, county)
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


def add_titles(county):
    _add_centered_title(
        "Social Connectedness Ranking Between US Counties and",
        above_the_drawing=1.1, fontsize=16
    )
    _add_centered_title(
        f"{county.name} (FIPS Code {county.fips})",
        above_the_drawing=1.03, fontsize=32
    )


def add_circle(ax, county):
    ax.add_artist(
        Circle(
            radius=100000,
            xy=(county.center.x, county.center.y),
            facecolor="None",
            edgecolor=SELECTED_COLOR,
            linewidth=4
        )
    )


def add_legend(data_breaks, county):
    data_breaks = [Patch(facecolor=c, edgecolor=EDGE_COLOR, label=text)
                   for _, c, text in data_breaks]
    selected_county = [Patch(facecolor=SELECTED_COLOR, edgecolor=EDGE_COLOR, label=county.name)]
    patches = selected_county + data_breaks

    _ = plt.legend(
        handles=patches,
        bbox_to_anchor=(0.5, 0.98), loc='center',
        ncol=10, fontsize=14, columnspacing=1,
        handlelength=1, handleheight=1,
        edgecolor=BACKGROUND_COLOR,
        handletextpad=0.4
    )
