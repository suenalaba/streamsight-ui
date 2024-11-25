from typing import Dict, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


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
