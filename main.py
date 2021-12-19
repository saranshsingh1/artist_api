from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, url_for
from flask_pymongo import PyMongo
from pymongo.errors import OperationFailure


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/songs_db"
mongodb_client = PyMongo(app)
db = mongodb_client.db


# Temporary cache to house the data for quick access
cache = {
    "difficulty": {},
    "search_words": {},
    "ratings": {},
}


@app.route("/songs")
def list_songs():
    """
    Returns a list of songs with the data provided by the "songs.json".

    - Add a way to paginate songs.
    """

    max_songs_per_page: int = 5
    after = request.args.get("after")

    # Check for a valid value of 'after' if it exists
    try:
        after_id = ObjectId(after) if after is not None else None
    except InvalidId:
        return {"error": f"Invalid 'after' value '{after}' provided."}, 400

    # Add limiting filters to the 'find' method based on the after value.
    filters = {"_id": {"$gt": after_id}} if after_id else {}
    # Reference for find
    # - https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.find
    user_songs = db.songs.find(filters).limit(max_songs_per_page)

    db_songs = []
    for song in user_songs:
        # convert the ObjectId to a string for serialization
        song["_id"] = str(song["_id"])
        db_songs.append(song)

    if not db_songs:
        return {"songs": [], "_links": {}}

    # Use the last song's id from the list as the anchor
    # to fetch the next set of songs for the next page.
    last_song_id = str(db_songs[-1]["_id"])

    links = {"self": {"href": url_for("list_songs", after=after, _external=True)}}

    # Add the next link only if the result is at least equal to max result per page.
    if len(db_songs) >= max_songs_per_page:
        links.update(
            next={"href": url_for("list_songs", after=last_song_id, _external=True)}
        )

    return {"songs": db_songs, "_links": links}


@app.route("/average_difficulty")
def list_average_difficulty_levels():
    """
    Returns the average difficulty for all songs.

    - Takes an optional parameter "level" to filter for only songs
      from a specific level.
    """

    # Check for level value in the query parameters
    try:
        # Convert the value to a float.
        difficulty_level = float(request.args.get("level"))
    except ValueError:
        # ValueError occurs if we cannot cast value to float.
        return {"error": "Please provide a numerical value for difficulty level."}, 400
    except TypeError:
        # TypeError occurs for None values of `level`
        difficulty_level = "base"

    # Check if the data exists in the cache
    if difficulty_level in cache["difficulty"]:
        return {
            "difficulty_level": "All levels"
            if difficulty_level == "base"
            else f"Level {int(difficulty_level)} and above",
            "average_difficulty": cache["difficulty"][difficulty_level],
        }

    # We need only the 'difficulty' data from the collection.
    propagation = {"difficulty": 1, "_id": 0}

    # Apply the filter if provided; else get everything
    if difficulty_level and difficulty_level != "base":
        data = db.songs.find({"difficulty": {"$gte": difficulty_level}}, propagation)
    else:
        data = db.songs.find({}, propagation)

    # Get the data from the Cursor object.
    diff_level_data = [song["difficulty"] for song in data]

    if not diff_level_data:
        return {"message": "No songs found to assess difficulty"}

    average_difficulty = round(sum(diff_level_data) / len(diff_level_data), 2)

    # Save the data to a cache for a certain fixed amount of time.
    cache["difficulty"][difficulty_level] = average_difficulty

    return {
        "difficulty_level": "All levels"
        if difficulty_level == "base"
        else f"Level {int(difficulty_level)} and above",
        "average_difficulty": average_difficulty,
    }


@app.route("/songs/<string:search_word>")
def get_song(search_word: str):
    """
    Returns a list of songs matching the search string.

    - Takes a required parameter "message" containing the user's search string.
    - The search should take into account song's artist and title.
    - The search should be case insensitive.
    """

    if search_word.lower() in cache["search_words"]:
        return {"songs": cache["search_words"][search_word.lower()]}

    # Use the $text search option by indexing the artist and title attributes.
    # Reference -> https://docs.mongodb.com/manual/core/index-text/
    result = db.songs.find({"$text": {"$search": search_word.lower()}})

    db_songs = []

    try:
        for song in result:
            song["_id"] = str(song["_id"])
            db_songs.append(song)
    except OperationFailure:
        # Should occur when there are no songs (empty db) to use `$text` search
        # Exception - text index required for $text query
        #             (no such collection 'songs_db.songs').
        return {"message": f"No songs found for '{search_word}' value."}

    # If no songs found for the search_word, return the same message as above.
    if not db_songs:
        return {"message": f"No songs found for '{search_word}' value."}

    cache["search_words"][search_word.lower()] = db_songs

    return {"songs": db_songs}


@app.route("/ratings", methods=["PUT"])
def add_rating_to_song():
    """
    Adds a rating for the given song.

    - Takes required parameters "song_id" and "rating".
    - Ratings should be between 1 and 5 inclusive.
    """

    data = request.get_json()
    song_id = data.get("song_id")

    if song_id is None:
        return {"error": "Please provide a song id."}, 400

    try:
        object_id = ObjectId(song_id)
    except InvalidId:
        return {"error": f"Invalid song_id '{song_id}' provided."}, 400

    try:
        rating_value = float(data.get("rating"))
    except TypeError:
        # Occurs if no (None) value is provided for `rating`
        return {"error": "Please provide a rating value for the song."}, 404
    except ValueError:
        # Occurs if the rating value cannot be cast to a float
        return {"error": "Please provide a valid numerical rating for the song."}, 400

    if rating_value < 1 or rating_value > 5:
        return {"error": "Please provide a rating between 1 and 5."}, 400

    # Reference for mongodb push on arrays
    # - https://docs.mongodb.com/manual/reference/operator/update/push/
    # NOTE: Either an update occurs or nothing gets modified.
    db.songs.update_one({"_id": object_id}, {"$push": {"ratings": rating_value}})

    return jsonify(""), 204


@app.route("/ratings/<string:song_id>")
def list_song_rating_stats(song_id: str):
    """
    Returns the average, the lowest and the highest rating
    of the given song id.
    """

    # Ensure the song id can be validated before proceeding further.
    try:
        object_id = ObjectId(song_id)
    except InvalidId:
        return {"error": f"Invalid song_id '{song_id}' provided."}, 400

    if song_id in cache["ratings"]:
        return {"_id": song_id, **cache["ratings"][song_id]}

    # Get only the ratings data using the 'projection' option
    #  - https://docs.mongodb.com/drivers/node/current/usage-examples/findOne/
    song_data = db.songs.find_one({"_id": object_id}, {"ratings": 1, "_id": 0})

    # None is returned if no song is found with the requested object id.
    if song_data is None:
        return {"message": f"Did not find the song with id: '{song_id}'."}, 404

    song_rating = song_data.get("ratings")
    # We get an empty dictionary if no ratings are found
    if not song_rating:
        return {"message": f"No ratings found for song id '{song_id}'"}, 404

    average, lowest, highest = (
        sum(song_rating) / len(song_rating),
        min(song_rating),
        max(song_rating),
    )

    # Store the data in a cache that can be periodically evicted.
    cache["ratings"][song_id]: dict = {
        "average_rating": round(average, 2),
        "lowest_rating": round(lowest, 2),
        "highest_rating": round(highest, 2),
    }

    return {"_id": song_id, **cache["ratings"][song_id]}
