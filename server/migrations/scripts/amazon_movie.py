import gzip
import os
import shutil
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import requests
from sqlalchemy import JSON, Column, Engine
from sqlmodel import Field, Session, SQLModel, create_engine

from migrations.utils.preprocess_df import map_user_and_item_ids

DATASET_URL = "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_v2/metaFiles2/meta_Movies_and_TV.json.gz"
ZIP_PATH = "migrations/datasets/meta_Movies_and_TV.json.gz"
FILENAMES = ["meta_Movies_and_TV.json"]
DATASET_DIR = "migrations/datasets"
EXTRACTED_DATASETS_PATH = "migrations/datasets"
_ENGINE: Engine = None
CONNECTION_STRING = "postgresql://localhost:5432/streamsight_test"

INTERACTION_DATASET_URL = "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_v2/categoryFilesSmall/Movies_and_TV.csv"
INTERACTION_ZIP_PATH = "migrations/datasets/Movies_and_TV.csv"
INTERACTION_FILENAMES = ["Movies_and_TV.csv"]


class AmazonMovieItem(SQLModel, table=True):
    category: List[str] = Field(default=None, sa_column=Column(JSON))
    description: List[str] = Field(default=None, sa_column=Column(JSON))
    title: str
    also_buy: List[str] = Field(default=None, sa_column=Column(JSON))
    brand: str
    feature: List[str] = Field(default=None, sa_column=Column(JSON))
    rank: str
    also_view: List[str] = Field(default=None, sa_column=Column(JSON))
    main_cat: str
    price: str
    asin: int = Field(primary_key=True)
    imageURL: List[str] = Field(default=None, sa_column=Column(JSON))
    imageURLHighRes: List[str] = Field(default=None, sa_column=Column(JSON))
    details: Optional[Dict] = Field(default=None, sa_column=Column(JSON))

    # Needed for Column(JSON)
    class Config:
        arbitrary_types_allowed = True


def main():
    try:
        download_dataset()
        extract_files()
        interaction_df = get_interaction_dataframe()
        _, item_id_mapping = map_user_and_item_ids(
            interaction_df, "user_id", "item_id", "timestamp"
        )
        items = read_items_attributes(item_id_mapping)
        with Session(get_sql_connection()) as session:
            session.add_all(items)
            session.commit()
        clean_up()
    except Exception as e:
        print("Error storing data for amazon_movie dataset: ", e)


def download_dataset():
    response = requests.get(DATASET_URL)

    with open(ZIP_PATH, "wb") as file:
        file.write(response.content)

    print("Download completed.")


def extract_files():
    for file_name in FILENAMES:
        file_path = ZIP_PATH
        extract_path = f"{DATASET_DIR}/{file_name}"

        with gzip.open(file_path, "rb") as f_in, open(extract_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        print(f"Extracted {file_name} to {DATASET_DIR}")


def get_sql_connection() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(CONNECTION_STRING)
        SQLModel.metadata.create_all(_ENGINE)
    return _ENGINE


def get_interaction_dataframe() -> pd.DataFrame:
    if not os.path.exists(INTERACTION_ZIP_PATH):
        response = requests.get(INTERACTION_DATASET_URL)
        with open(INTERACTION_ZIP_PATH, "wb") as file:
            file.write(response.content)
        print("Downloaded interaction dataset.")
    df = pd.read_csv(
        INTERACTION_ZIP_PATH,
        dtype={
            "item_id": str,
            "user_id": str,
            "rating": np.float32,
            "timestamp": np.int64,
        },
        names=["item_id", "user_id", "rating", "timestamp"],
    )
    return df


def read_items_attributes(item_id_mapping: Dict[str, int]) -> List[AmazonMovieItem]:
    df = pd.read_json(DATASET_DIR + "/" + FILENAMES[0], lines=True)
    df = df.drop(columns=["tech1", "tech2", "fit", "date", "similar_item"])

    df = df.drop_duplicates(subset="asin")

    # 'asin' is item_id in this case so map to our internal mappings
    df["asin"] = df["asin"].astype(str)
    df["asin"] = df["asin"].map(item_id_mapping)
    df = df.dropna(subset=["asin"])
    df["asin"] = df["asin"].astype(int)

    # map arrays of old item_ids to new item_ids
    def map_item_ids(item_ids: List[str]) -> List[int]:
        if not isinstance(item_ids, list):
            return []
        return [
            item_id_mapping.get(str(item_id))
            for item_id in item_ids
            if item_id_mapping.get(str(item_id)) is not None
        ]

    df["also_buy"] = df["also_buy"].apply(map_item_ids)
    df["also_view"] = df["also_view"].apply(map_item_ids)

    # replace NaN with None
    df.replace({np.nan: None}, inplace=True)

    items = [AmazonMovieItem(**row.to_dict()) for _, row in df.iterrows()]
    return items


def clean_up():
    delete_extracted_files()


def delete_extracted_files():
    if os.path.exists(EXTRACTED_DATASETS_PATH):
        for filename in os.listdir(EXTRACTED_DATASETS_PATH):
            file_path = os.path.join(EXTRACTED_DATASETS_PATH, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        print(f"Deleted all files in folder: {EXTRACTED_DATASETS_PATH}")


if __name__ == "__main__":
    main()
