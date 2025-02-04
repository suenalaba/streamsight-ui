import csv
import os
import shutil
import zipfile
from typing import Dict, List

import pandas as pd
import requests
from sqlalchemy import Engine
from sqlmodel import Field, Session, SQLModel, create_engine

from migrations.constants import CONNECTION_STRING
from migrations.utils.preprocess_df import map_user_and_item_ids

DATASET_URL = "http://files.grouplens.org/datasets/movielens/ml-100k.zip"
ZIP_PATH = "migrations/datasets/ml-100k.zip"
DATASET_DIR = "migrations/datasets"
EXTRACTED_DATASETS_PATH = "migrations/datasets/ml-100k"
FILENAMES = ["ml-100k/u.user", "ml-100k/u.item", "ml-100k/u.data"]
_ENGINE: Engine = None


class MovieLens100kUser(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    age: int
    gender: str
    occupation: str
    zip_code: str


class MovieLens100kItem(SQLModel, table=True):
    movie_id: int = Field(primary_key=True)
    title: str
    release_date: str
    video_release_date: str
    imdb_url: str
    unknown: bool = Field(default=False)
    action: bool = Field(default=False)
    adventure: bool = Field(default=False)
    animation: bool = Field(default=False)
    children: bool = Field(default=False)
    comedy: bool = Field(default=False)
    crime: bool = Field(default=False)
    documentary: bool = Field(default=False)
    drama: bool = Field(default=False)
    fantasy: bool = Field(default=False)
    film_noir: bool = Field(default=False)
    horror: bool = Field(default=False)
    musical: bool = Field(default=False)
    mystery: bool = Field(default=False)
    romance: bool = Field(default=False)
    sci_fi: bool = Field(default=False)
    thriller: bool = Field(default=False)
    war: bool = Field(default=False)
    western: bool = Field(default=False)


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
        with Session(get_sql_connection()) as session:
            session.add_all(users)
            session.add_all(items)
            session.commit()
        clean_up()
    except Exception as e:
        print("Error storing data for movielens100k dataset: ", e)


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
    with open(EXTRACTED_DATASETS_PATH + "/u.data", "r") as file:
        rows = csv.reader(file, delimiter="\t")
        interactions = [
            (int(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in rows
        ]
        df = pd.DataFrame(
            interactions, columns=["user_id", "item_id", "rating", "timestamp"]
        )
        return df


def read_users_attributes(user_id_mapping: Dict[int, int]) -> List[MovieLens100kUser]:
    with open(EXTRACTED_DATASETS_PATH + "/u.user", "r") as file:
        rows = csv.reader(file, delimiter="|")
        users = [
            MovieLens100kUser(
                user_id=user_id_mapping[int(row[0])],
                age=int(row[1]),
                gender=row[2],
                occupation=row[3],
                zip_code=row[4],
            )
            for row in rows
        ]
        return users


def read_items_attributes(item_id_mapping: Dict[int, int]) -> List[MovieLens100kItem]:
    with open(EXTRACTED_DATASETS_PATH + "/u.item", "r", encoding="ISO-8859-1") as file:
        rows = csv.reader(file, delimiter="|")
        movies = []
        for row in rows:
            genres = row[5:]
            movie = MovieLens100kItem(
                movie_id=item_id_mapping[int(row[0])],
                title=row[1],
                release_date=row[2],
                video_release_date=row[3],
                imdb_url=row[4],
                unknown=int(genres[0]) == 1,
                action=int(genres[1]) == 1,
                adventure=int(genres[2]) == 1,
                animation=int(genres[3]) == 1,
                children=int(genres[4]) == 1,
                comedy=int(genres[5]) == 1,
                crime=int(genres[6]) == 1,
                documentary=int(genres[7]) == 1,
                drama=int(genres[8]) == 1,
                fantasy=int(genres[9]) == 1,
                film_noir=int(genres[10]) == 1,
                horror=int(genres[11]) == 1,
                musical=int(genres[12]) == 1,
                mystery=int(genres[13]) == 1,
                romance=int(genres[14]) == 1,
                sci_fi=int(genres[15]) == 1,
                thriller=int(genres[16]) == 1,
                war=int(genres[17]) == 1,
                western=int(genres[18]) == 1,
            )
            movies.append(movie)
        return movies


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
        shutil.rmtree(EXTRACTED_DATASETS_PATH)
        print(f"Deleted folder: {EXTRACTED_DATASETS_PATH}")
    else:
        print("Folder does not exist.")


if __name__ == "__main__":
    main()
