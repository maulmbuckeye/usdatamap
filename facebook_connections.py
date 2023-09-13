import pandas as pd
from os.path import isfile


class FacebookConnections:
    FACEBOOK_DATA_GZIP = "./data/county_county.gzip"
    FACEBOOK_DATA_TSV = "./data/county_county.tsv"

    def __init__(self):
        self.df = pd.DataFrame()
        self.get()

    def get_connections(self, fips: str) -> pd.DataFrame:
        return self.df[self.df.user_loc == fips]

    def get_number_of_connections_from_county(self, fips: str):
        return self.get_connections(fips).set_index("fr_loc").scaled_sci

    def get(self):
        if isfile(self.FACEBOOK_DATA_GZIP):
            print(f"Reading {self.FACEBOOK_DATA_GZIP} ... ", end='')
            self.df = pd.read_parquet(self.FACEBOOK_DATA_GZIP)  # noqa
            print("DONE")
        else:
            self._get_from_tsv()

    def _get_from_tsv(self):
        print(f"Reading {self.FACEBOOK_DATA_TSV} ... ", end='')
        df = pd.read_csv(self.FACEBOOK_DATA_TSV, sep="\t")     # noqa
        print("DONE")

        df.user_loc = ("0" + df.user_loc.astype(str)).str[-5:]
        df.fr_loc = ("0" + df.fr_loc.astype(str)).str[-5:]
        df.to_parquet(self.FACEBOOK_DATA_GZIP, compression="gzip")
        self.df = df
