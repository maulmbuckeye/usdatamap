from GeoConnect import GeoConnections


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
            random_county = geo_connect.get_random_county()
            geo_connect.plot_a_county(random_county)
        elif response == "refresh":
            geo_connect.get_data(try_cache=False)
        else:
            geo_connect.plot_a_county(response)


if __name__ == '__main__':
    main()
