from typing import Dict, Tuple

import pandas as pd


def map_user_and_item_ids(
    df: pd.DataFrame, user_ix: str, item_ix: str, timestamp_ix: str
) -> Tuple[Dict[int, int], Dict[int, int]]:
    """
    Update the USER_ID and ITEM_ID mapping to correspond to Streamsight.
    USER_ID and ITEM_ID should be 0-indexed and sorted according to timestamp

    :param df: Dataframe containing the user and item ids and timestamp. Can have additional columns which will be ignored.
    :type df: pd.DataFrame
    :param user_ix: Column name representing the user ids.
    :type user_ix: str
    :param item_ix: Column name representing the item ids.
    :type item_ix: str
    :param timestamp_ix: Column name representing the timestamp.
    :type timestamp_ix: str
    """
    # sort by timestamp
    df.sort_values(by=[timestamp_ix], inplace=True, ignore_index=True)

    user_index = pd.CategoricalIndex(df[user_ix], categories=df[user_ix].unique())
    user_id_mapping = {
        old_id: new_id for new_id, old_id in enumerate(user_index.drop_duplicates())
    }

    item_index = pd.CategoricalIndex(df[item_ix], categories=df[item_ix].unique())
    item_id_mapping = {
        old_id: new_id for new_id, old_id in enumerate(item_index.drop_duplicates())
    }

    return user_id_mapping, item_id_mapping


if __name__ == "__main__":
    input_dict = {
        "user_id": [1, 2, 3, 1, 2, 2, 4, 3, 3, 4, 5, 5, 5],
        "item_id": [1, 1, 2, 3, 2, 3, 2, 1, 3, 3, 1, 2, 3],
        "timestamp": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 10],
        "rating": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3],
    }

    df = pd.DataFrame.from_dict(input_dict)
    map_user_and_item_ids(df, "user_id", "item_id", "timestamp")
