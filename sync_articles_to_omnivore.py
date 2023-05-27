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

logging.basicConfig(level=logging.DEBUG)
omnivore = Omnivore()
pocket = Pocket()

def save_article(article, retry=3):
    if retry == 0:
        return None
    saved_page_id = omnivore.save_page(article["href"])
    logging.debug(f"(Save) Response: {saved_page_id}")
    # We need to wait a bit before updating the page
    time.sleep(5)
    if not saved_page_id:
        return save_article(article, retry - 1)
    logging.info(f"Uploaded")
    return saved_page_id


def update_article(page_id, article, retry=3):
    if retry == 0:
        return None
    updated = omnivore.update_page(
        page_id=page_id, date=article["time_added"], title=article["title"]
    )
    logging.debug(f"(Update) Response: {updated}")
    time.sleep(5)
    if not updated:
        return update_article(article, retry - 1)
    logging.info(f"Information updated")
    return updated


def archive_article(page_id, retry=3):
    if retry == 0:
        return None
    archived = omnivore.archive_page(id=page_id, status=True)
    logging.debug(f"(Archive) Response: {archived}")
    time.sleep(5)
    if not archived:
        return archive_article(page_id, retry - 1)
    logging.info(f"Article archived")
    return archived


def create_tag(tag, retry=3):
    if retry == 0:
        return None
    new_label = omnivore.create_label(
        name=tag,
        color=f"#{random.randint(0, 0xFFFFFF):06x}",
        description="",
    )
    logging.debug(f"(Create tag) Response: {new_label}")
    time.sleep(5)
    if not new_label:
        return create_tag(tag, retry - 1)
    logging.info(f"New tag created: ${tag}")
    return new_label


def set_tags(page_id, tags, retry=3):
    if retry == 0:
        return None
    set_label = omnivore.set_labels(page_id=page_id, label_ids=tags)
    logging.debug(f"(Set tag) Response: {set_label}")
    time.sleep(5)
    if not set_label:
        return set_tags(page_id, tag, retry - 1)
    logging.info(f"Tags set: ${tags}")
    return set_label


def pocket_to_omnivore():
    labels = omnivore.get_labels()
    total_rows = pocket.content.shape[0]
    for i, article in pocket.content.iterrows():
        logging.info(
            f"Next article to upload ({i+1}/{total_rows}) => {article['title']}"
        )
        saved_page_id = save_article(article)
        if not saved_page_id:
            continue
        updated = update_article(saved_page_id, article)
        if article["read"]:
            archived = archive_article(saved_page_id)
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
                    new_label = create_tag(tag)
                    if not new_label:
                        continue
                    labels.append(new_label)
                    label_id = new_label["id"]
                # Collect labels to insert
                labels_to_insert.append(label_id)
            # Insert all labels at once
            set_label = set_tags(saved_page_id, labels_to_insert)

if __name__ == "__main__":
    pocket_to_omnivore()
