import json
import pymongo
from pymongo import MongoClient


def delete_database(url="mongodb://localhost:27017/songs_db"):
    MongoClient(url).drop_database("songs_db")


def add_data(url="mongodb://localhost:27017/songs_db"):
    mongodb_client = MongoClient(url)
    db = mongodb_client["songs_db"]
    songs_collection = db.songs

    songs = []
    with open("songs.json") as file:
        for line in file.readlines():
            songs.append(json.loads(line.strip()))

    # Index the metadata attributes 'artist_lower' and 'title_lower'
    # for text search option. https://docs.mongodb.com/manual/text-search/#text-index
    songs_collection.create_index([("artist", pymongo.TEXT), ("title", pymongo.TEXT)])
    songs_collection.insert_many(songs)


if __name__ == "__main__":
    delete_database()
    add_data()
