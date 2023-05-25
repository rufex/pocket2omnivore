import json
import logging
import os
import random
import time
from pathlib import Path
from random import randint
from typing import List

from dotenv import load_dotenv

from omnivore import Omnivore
from pocket import Pocket

load_dotenv()


def pocket_to_omnivore():
    logging.basicConfig(level=logging.INFO)
    omnivore = Omnivore()
    pocket = Pocket()
    labels = omnivore.get_labels()
    total_rows = pocket.content.shape[0]
    for i, article in pocket.content.iterrows():
        logging.info(
            f"Next article to upload ({i+1}/{total_rows}) => {article['title']}"
        )
        saved_page_id = omnivore.save_page(article["href"])
        logging.info(f"Uploaded")
        # We need to wait a bit before updating the page
        time.sleep(4)
        update = omnivore.update_page(
            page_id=saved_page_id, date=article["time_added"], title=article["title"]
        )
        logging.info(f"Information updated")
        if article["read"]:
            omnivore.archive_page(id=saved_page_id, status=True)
            logging.info(f"Article archived")
            time.sleep(2)
        if article["tags"]:
            tags = article["tags"].split(",")
            labels_to_insert = []
            for tag in tags:
                label_id = None
                # Check if tag already exists
                for label in labels:
                    if label["name"].lower() == tag:
                        label_id = label["id"]
                        break
                # Create missing tag
                if not label_id:
                    new_label = omnivore.create_label(
                        name=tag,
                        color=f"#{random.randint(0, 0xFFFFFF):06x}",
                        description="",
                    )
                    logging.info(f"New tag created: ${tag}")
                    time.sleep(2)
                    labels.append(new_label)
                    label_id = new_label["id"]
                # Collect labels to insert
                labels_to_insert.append(label_id)
            # Insert all labels at once
            omnivore.set_labels(page_id=saved_page_id, label_ids=labels_to_insert)
            logging.info(f"Tags inserted")
            time.sleep(2)


if __name__ == "__main__":
    pocket_to_omnivore()
