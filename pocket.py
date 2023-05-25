from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

FILE_PATH = Path("./pocket_export/ril_export.html")


# content: dataframe containing all articles
# content.dtypes
# read                    bool
# time_added    datetime64[ns]
# href                  object
# tags                  object
# title                 object
class Pocket:
    def __init__(self) -> None:
        self.content = self.open_file()

    def open_file(self) -> pd.DataFrame:
        with open(FILE_PATH, "r") as f:
            soup = BeautifulSoup(f, "html.parser")
            sections = soup.findAll("h1")  # Unread // Read Archive
            df = pd.concat([self.process_section(section) for section in sections])
            return df

    def process_section(self, h1) -> pd.DataFrame:
        ul = h1.find_next_sibling("ul")
        read = h1.text != "Unread"
        items = []
        for a in ul.findAll("a", href=True):
            items.append(
                {
                    "read": read,
                    "time_added": a["time_added"],
                    "href": a["href"],
                    "tags": a["tags"],
                    "title": a.text,
                }
            )

        df = pd.DataFrame(items)
        df["time_added"] = pd.to_datetime(df["time_added"], unit="s")
        return df
