import csv
import os
import zipfile
from typing import Dict, List

import pandas as pd
import requests
from sqlalchemy import Engine
from sqlmodel import Field, Session, SQLModel, create_engine

from migrations.utils.preprocess_df import map_user_and_item_ids
from migrations.constants import CONNECTION_STRING

DATASET_URL = "https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-2k.zip"
ZIP_PATH = "migrations/datasets/hetrec2011-lastfm-2k.zip"
FILENAMES = [
    "artists.dat",
    "tags.dat",
    "user_taggedartists-timestamps.dat",
    "user_friends.dat",
]
DATASET_DIR = "migrations/datasets"
EXTRACTED_DATASETS_PATH = "migrations/datasets"
_ENGINE: Engine = None


class LastFM2kUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    friend_id: int


class LastFM2kItem(SQLModel, table=True):
    item_id: int = Field(primary_key=True)
    name: str
    url: str
    picture_url: str


class LastFM2kTag(SQLModel, table=True):
    tag_id: int = Field(primary_key=True)
    tag_value: str


def main():
    try:
        download_dataset()
        extract_files()
        df = get_interaction_dataframe()
        user_id_mapping, item_id_mapping = map_user_and_item_ids(
            df, "user_id", "item_id", "timestamp"
        )
        users = read_users_attributes(user_id_mapping)
        items = read_items_attributes(item_id_mapping)
        tags = read_tag_attributes()
        with Session(get_sql_connection()) as session:
            session.add_all(users)
            session.add_all(items)
            session.add_all(tags)
            session.commit()
        clean_up()
    except Exception as e:
        print("Error storing data for lastfm2k dataset: ", e)


def download_dataset():
    response = requests.get(DATASET_URL)

    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"Created directory: {DATASET_DIR}")
        
    with open(ZIP_PATH, "wb") as file:
        file.write(response.content)

    print("Download completed.")


def extract_files():
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        for file_name in FILENAMES:
            zip_ref.extract(file_name, path=DATASET_DIR)
            print(f"Extracted {file_name} to {DATASET_DIR}")


def get_sql_connection() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(CONNECTION_STRING)
        SQLModel.metadata.create_all(_ENGINE)
    return _ENGINE


def get_interaction_dataframe() -> pd.DataFrame:
    with open(
        EXTRACTED_DATASETS_PATH + "/user_taggedartists-timestamps.dat", "r"
    ) as file:
        rows = csv.reader(file, delimiter="\t")

        next(rows)  # skip header row

        interactions = [
            (int(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in rows
        ]
        df = pd.DataFrame(
            interactions, columns=["user_id", "item_id", "tag_id", "timestamp"]
        )
        return df


def read_users_attributes(user_id_mapping: Dict[int, int]) -> List[LastFM2kUser]:
    with open(EXTRACTED_DATASETS_PATH + "/user_friends.dat", "r") as file:
        rows = csv.reader(file, delimiter="\t")

        next(rows)  # skip header row

        users = [
            LastFM2kUser(
                user_id=user_id_mapping[int(row[0])],
                friend_id=user_id_mapping[int(row[1])],
            )
            for row in rows
            if user_id_mapping.get(int(row[0])) is not None
            and user_id_mapping.get(int(row[1])) is not None
        ]

        return users


def read_items_attributes(item_id_mapping: Dict[int, int]) -> List[LastFM2kItem]:
    with open(EXTRACTED_DATASETS_PATH + "/artists.dat", "r") as file:
        rows = csv.reader(file, delimiter="\t")

        next(rows)  # skip header row

        items = [
            LastFM2kItem(
                item_id=item_id_mapping[int(row[0])],
                name=row[1],
                url=row[2],
                picture_url=row[3],
            )
            for row in rows
            if item_id_mapping.get(int(row[0])) is not None
        ]
        return items


def read_tag_attributes() -> List[LastFM2kTag]:
    with open(
        EXTRACTED_DATASETS_PATH + "/tags.dat", "r", encoding="ISO-8859-1"
    ) as file:
        rows = csv.reader(file, delimiter="\t")

        next(rows)  # skip header row

        tags = [LastFM2kTag(tag_id=int(row[0]), tag_value=row[1]) for row in rows]
        return tags


def clean_up():
    delete_zip_file()
    delete_extracted_files()


def delete_zip_file():
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
        print(f"Deleted zip file: {ZIP_PATH}")
    else:
        print("Zip File does not exist.")


def delete_extracted_files():
    if os.path.exists(EXTRACTED_DATASETS_PATH):
        for filename in os.listdir(EXTRACTED_DATASETS_PATH):
            file_path = os.path.join(EXTRACTED_DATASETS_PATH, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        print(f"Deleted all files in folder: {EXTRACTED_DATASETS_PATH}")
    else:
        print("Folder does not exist.")


if __name__ == "__main__":
    main()
