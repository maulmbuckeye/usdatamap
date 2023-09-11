import seaborn as sns
import matplotlib.pyplot as plt


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

    plt.axis("off")
    plt.show()
