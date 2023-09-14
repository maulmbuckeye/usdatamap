from GeoConnect import GeoConnections
import argparse


def main():
    is_using_random_selection = get_parameters()
    geo_connect = GeoConnections(try_cache=True)
    if is_using_random_selection:
        geo_connect.plot_a_random_county()
    else:
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
            geo_connect.plot_a_random_county()
        elif response == "refresh":
            geo_connect.get_data(try_cache=False)
        else:
            geo_connect.plot_a_county(response)


def get_parameters(argv=None) -> bool:
    parser = argparse.ArgumentParser(description='Create a Social Connectedness map of the US.')
    parser.add_argument('-r','--random',
                        help='use a random county',
                        action='store_true')
    args = parser.parse_args(argv)
    return args.random


if __name__ == '__main__':
    main()
