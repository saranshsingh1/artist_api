import json
import unittest

from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from _pytest.monkeypatch import MonkeyPatch

import main
from import_data import add_data, delete_database


class TestEmptyDB(unittest.TestCase):
    """Test suite for an empty database."""

    def setUp(self):
        self.app = main.app
        self.app.testing = True
        self.app.MONGO_URI = "mongodb://localhost:27017/test_db"
        self.db = PyMongo(self.app).db
        self.client = self.app.test_client()

    def test_empty_list_songs_route(self):
        response = self.client.get("/songs")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("_links", response.json)
        self.assertIn("songs", response.json)

        self.assertEqual(response.json["songs"], [])
        self.assertEqual(response.json["_links"], {})

    def test_empty_list_average_difficulty_route_basic(self):
        response = self.client.get("/average_difficulty")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], "No songs found to assess difficulty"
        )
        self.assertEqual(
            json.loads(response.data),
            {"message": "No songs found to assess difficulty"},
        )

    def test_empty_list_average_difficulty_route_with_invalid_level(self):
        response = self.client.get("/average_difficulty?level=test")

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"],
            "Please provide a numerical value for difficulty level.",
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a numerical value for difficulty level."},
        )

    def test_empty_list_average_difficulty_route_with_valid_level(self):
        response = self.client.get("/average_difficulty?level=10")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], "No songs found to assess difficulty"
        )
        self.assertEqual(
            json.loads(response.data),
            {"message": "No songs found to assess difficulty"},
        )

    def test_empty_get_song_based_on_no_string_route(self):
        response = self.client.get("/songs/")

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    def test_empty_get_song_based_on_string_route(self):
        string_value = "test"
        response = self.client.get(f"/songs/{string_value}")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], f"No songs found for '{string_value}' value."
        )

        self.assertEqual(
            json.loads(response.data),
            {"message": f"No songs found for '{string_value}' value."},
        )

    def test_empty_add_ratings_route_with_no_song_id(self):
        response = self.client.put("/ratings", json={"no_song_id": "asd_wed"})

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Please provide a song id.")

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a song id."},
        )

    def test_empty_add_ratings_with_invalid_song_id_route(self):
        song_id = "asd_wed"
        response = self.client.put("/ratings", json={"song_id": song_id})

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], f"Invalid song_id '{song_id}' provided."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": f"Invalid song_id '{song_id}' provided."},
        )

    def test_empty_add_ratings_with_valid_song_id_and_invalid_rating_route(self):
        response = self.client.put("/ratings", json={"song_id": str(ObjectId())})

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating value for the song."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating value for the song."},
        )

        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": None}
        )

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating value for the song."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating value for the song."},
        )

        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": "bad_rating"}
        )

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"],
            "Please provide a valid numerical rating for the song.",
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a valid numerical rating for the song."},
        )

        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": 0}
        )

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating between 1 and 5."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating between 1 and 5."},
        )

    def test_empty_add_ratings_with_valid_song_id_and_rating_route(self):
        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": 1}
        )

        self.assertEqual(response.status, "204 NO CONTENT")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.data, bytes)
        self.assertEqual(response.data, b"")

    def test_empty_list_song_rating_stats_invalid_song_id_route(self):
        song_id = "abc_xyz"
        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], f"Invalid song_id '{song_id}' provided."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": f"Invalid song_id '{song_id}' provided."},
        )

    def test_empty_list_song_rating_stats_valid_song_id_route(self):
        song_id = str(ObjectId())
        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], f"Did not find the song with id: '{song_id}'."
        )

        self.assertEqual(
            json.loads(response.data),
            {"message": f"Did not find the song with id: '{song_id}'."},
        )

    def tearDown(self):
        self.db.songs.delete_many({})
        del self.client
        del self.app


# ==================================================================================================
# ==================================================================================================
# ==================================================================================================


class TestAPIs(unittest.TestCase):
    """Regular Test suite."""

    def setUp(self):
        self.mongo_url = "mongodb://localhost:27017/test_db"
        self.app = main.app
        self.app.testing = True
        self.app.MONGO_URI = self.mongo_url
        add_data(self.mongo_url)
        self.db = PyMongo(self.app).db
        self.client = self.app.test_client()

    def test_list_songs_bad_after_route(self):
        after_value = "some_invalid_value"
        response = self.client.get(f"/songs?after={after_value}")

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"],
            f"Invalid 'after' value '{after_value}' provided.",
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": f"Invalid 'after' value '{after_value}' provided."},
        )

    def test_list_songs_route(self):
        response = self.client.get("/songs")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("_links", response.json)
        self.assertIn("next", response.json["_links"])
        self.assertIn("href", response.json["_links"]["next"])
        self.assertIn("self", response.json["_links"])
        self.assertIn("href", response.json["_links"]["self"])

        self.assertIn("songs", response.json)
        self.assertIn("_id", response.json["songs"][0])
        self.assertIn("artist", response.json["songs"][0])
        self.assertIn("difficulty", response.json["songs"][0])
        self.assertIn("level", response.json["songs"][0])
        self.assertIn("released", response.json["songs"][0])
        self.assertIn("title", response.json["songs"][0])

    def test_list_average_difficulty_route_with_invalid_level(self):
        response = self.client.get("/average_difficulty?level=test")

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"],
            "Please provide a numerical value for difficulty level.",
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a numerical value for difficulty level."},
        )

    def test_list_average_difficulty_route_basic(self):
        response = self.client.get("/average_difficulty")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("difficulty_level", response.json)
        self.assertIn("average_difficulty", response.json)

        self.assertEqual(response.json["difficulty_level"], "All levels")
        self.assertEqual(response.json["average_difficulty"], 10.32)
        self.assertEqual(
            json.loads(response.data),
            {"average_difficulty": 10.32, "difficulty_level": "All levels"},
        )

    def test_list_average_difficulty_route_with_difficulty_level(self):
        response = self.client.get("/average_difficulty?level=10")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("difficulty_level", response.json)
        self.assertIn("average_difficulty", response.json)

        self.assertEqual(response.json["difficulty_level"], "Level 10 and above")
        self.assertEqual(response.json["average_difficulty"], 13.58)
        self.assertEqual(
            json.loads(response.data),
            {"average_difficulty": 13.58, "difficulty_level": "Level 10 and above"},
        )

    def test_list_average_difficulty_route_with_large_difficulty_level(self):
        response = self.client.get("/average_difficulty?level=20")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], "No songs found to assess difficulty"
        )
        self.assertEqual(
            json.loads(response.data),
            {"message": "No songs found to assess difficulty"},
        )

    def test_get_song_for_no_string_route(self):
        response = self.client.get("/songs/")

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    def test_get_song_based_on_fake_string_route(self):
        string_value = "fake_word"
        response = self.client.get(f"/songs/{string_value}")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], f"No songs found for '{string_value}' value."
        )

        self.assertEqual(
            json.loads(response.data),
            {"message": f"No songs found for '{string_value}' value."},
        )

    def test_get_song_based_on_valid_string_route(self):
        string_value = "yousicians"
        response = self.client.get(f"/songs/{string_value}")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("songs", response.json)
        self.assertIsInstance(response.json["songs"], list)

        self.assertIn("_id", response.json["songs"][0])
        self.assertIn("artist", response.json["songs"][0])
        self.assertIn("difficulty", response.json["songs"][0])
        self.assertIn("level", response.json["songs"][0])
        self.assertIn("released", response.json["songs"][0])
        self.assertIn("title", response.json["songs"][0])

    def test_add_rating_to_song_route_with_no_song_id(self):
        response = self.client.put("/ratings", json={"no_song_id": "bad_song"})

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Please provide a song id.")
        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a song id."},
        )

    def test_add_rating_to_song_with_invalid_song_id_route(self):
        song_id = "not_an_id"
        response = self.client.put("/ratings", json={"song_id": song_id})

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], f"Invalid song_id '{song_id}' provided."
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": f"Invalid song_id '{song_id}' provided."},
        )

    def test_add_rating_to_song_with_valid_song_id_and_bad_data_rating_route(self):

        # missing rating
        response = self.client.put("/ratings", json={"song_id": str(ObjectId())})

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating value for the song."
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating value for the song."},
        )

        # explicitly send 'None' value
        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": None}
        )

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating value for the song."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating value for the song."},
        )

        # explicitly send inconvertible to float value
        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": "bad_rating"}
        )

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"],
            "Please provide a valid numerical rating for the song.",
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a valid numerical rating for the song."},
        )

        # rating less than 1
        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": 0}
        )

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating between 1 and 5."
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating between 1 and 5."},
        )

        # rating greater than 5
        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": 6}
        )

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "Please provide a rating between 1 and 5."
        )

        self.assertEqual(
            json.loads(response.data),
            {"error": "Please provide a rating between 1 and 5."},
        )

    def test_add_rating_to_song_with_valid_song_id_and_rating_route(self):

        response = self.client.put(
            "/ratings", json={"song_id": str(ObjectId()), "rating": 3}
        )

        self.assertEqual(response.status, "204 NO CONTENT")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.data, bytes)
        self.assertEqual(response.data.decode(), "")

    def test_list_song_rating_stats_with_invalid_song_id_route(self):
        song_id = "bad_song_id"
        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "400 BAD REQUEST")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], f"Invalid song_id '{song_id}' provided."
        )
        self.assertEqual(
            json.loads(response.data),
            {"error": f"Invalid song_id '{song_id}' provided."},
        )

    def test_list_song_rating_stats_valid_song_id_not_in_db_route(self):
        song_id = str(ObjectId())
        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], f"Did not find the song with id: '{song_id}'."
        )
        self.assertEqual(
            json.loads(response.data),
            {"message": f"Did not find the song with id: '{song_id}'."},
        )

    def test_list_song_rating_stats_valid_song_id_no_ratings_in_db_route(self):
        # insert dummy data in db
        song_id = str(ObjectId())
        new_song = {
            "_id": ObjectId(song_id),
            "artist": "A new artist",
            "difficulty": 5,
            "level": 5,
            "released": "2021-01-01",
            "title": "A new hit song",
        }
        self.db.songs.insert_one(new_song)

        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "404 NOT FOUND")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("message", response.json)
        self.assertEqual(
            response.json["message"], f"No ratings found for song id '{song_id}'"
        )
        self.assertEqual(
            json.loads(response.data),
            {"message": f"No ratings found for song id '{song_id}'"},
        )

    def test_list_song_rating_stats_valid_song_id_ratings_in_db_route(self):
        # insert dummy data in db
        song_id = str(ObjectId())
        new_song = {
            "_id": ObjectId(song_id),
            "artist": "A new artist",
            "difficulty": 5,
            "level": 5,
            "released": "2021-01-01",
            "title": "A new hit song",
            "ratings": [4, 1, 3, 5, 3, 2, 5, 4, 3, 3, 2, 5, 1],
        }
        self.db.songs.insert_one(new_song)

        response = self.client.get(f"/ratings/{song_id}")

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)

        self.assertIn("_id", response.json)
        self.assertIn("average_rating", response.json)
        self.assertIn("lowest_rating", response.json)
        self.assertIn("highest_rating", response.json)

        self.assertEqual(
            response.json,
            {
                "_id": song_id,
                "average_rating": 3.15,
                "highest_rating": 5,
                "lowest_rating": 1,
            },
        )
        self.assertEqual(
            json.loads(response.data),
            {
                "_id": song_id,
                "average_rating": 3.15,
                "highest_rating": 5,
                "lowest_rating": 1,
            },
        )

    def tearDown(self):
        delete_database(self.mongo_url)
        del self.client
        del self.app


# ==================================================================================================
# ==================================================================================================
# ==================================================================================================


class TestCacheAPI(unittest.TestCase):
    """Tests runs to check if data is fetched from the cache"""

    def setUp(self) -> None:
        # create a monkey patch instance for testing
        self.monkeypatch = MonkeyPatch()
        self.cache_copy = main.cache.copy()

        self.app = main.app
        self.app.testing = True
        self.app.MONGO_URI = "mongodb://localhost:27017/test_db"
        self.db = PyMongo(self.app).db
        self.client = self.app.test_client()

    def test_cached_average_difficulty_level(self):
        # monkey patch the cache for the test case
        self.monkeypatch.setitem(main.cache, "difficulty", {"base": 13.4, 23: 42})

        response = self.client.get("/average_difficulty")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)
        self.assertIn("difficulty_level", response.json)
        self.assertIn("average_difficulty", response.json)
        self.assertEqual(
            response.json,
            {"difficulty_level": "All levels", "average_difficulty": 13.4},
        )

        response = self.client.get("/average_difficulty?level=23")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)
        self.assertIn("difficulty_level", response.json)
        self.assertIn("average_difficulty", response.json)
        self.assertEqual(
            response.json,
            {"difficulty_level": "Level 23 and above", "average_difficulty": 42},
        )

    def test_cache_get_song_for_search_word(self):
        # monkey patch the cache for the test case
        self.monkeypatch.setitem(
            main.cache,
            "search_words",
            {
                "test_1": [
                    {
                        "_id": 1,
                        "artist": 2,
                        "difficulty": 3,
                        "level": 4,
                        "released": 5,
                        "title": "song",
                    }
                ]
            },
        )

        response = self.client.get("/songs/Test_1")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)
        self.assertIn("songs", response.json)
        self.assertEqual(
            response.json,
            {
                "songs": [
                    {
                        "_id": 1,
                        "artist": 2,
                        "difficulty": 3,
                        "level": 4,
                        "released": 5,
                        "title": "song",
                    }
                ]
            },
        )

    def test_cache_list_song_rating_stats(self):

        song_id_1, song_id_2 = str(ObjectId()), str(ObjectId())

        # monkey patch the cache for the test case
        self.monkeypatch.setitem(
            main.cache,
            "ratings",
            {
                song_id_1: {
                    "average_rating": 1.5,
                    "lowest_rating": 1,
                    "highest_rating": 2,
                },
                song_id_2: {
                    "average_rating": 2,
                    "lowest_rating": 1,
                    "highest_rating": 3,
                },
            },
        )

        response = self.client.get(f"/ratings/{song_id_1}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)
        self.assertIn("_id", response.json)
        self.assertIn("average_rating", response.json)
        self.assertIn("lowest_rating", response.json)
        self.assertIn("highest_rating", response.json)
        self.assertEqual(
            response.json,
            {
                "_id": song_id_1,
                "average_rating": 1.5,
                "lowest_rating": 1,
                "highest_rating": 2,
            },
        )

        response = self.client.get(f"/ratings/{song_id_2}")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertIsInstance(response.json, dict)
        self.assertIn("_id", response.json)
        self.assertIn("average_rating", response.json)
        self.assertIn("lowest_rating", response.json)
        self.assertIn("highest_rating", response.json)
        self.assertEqual(
            response.json,
            {
                "_id": song_id_2,
                "average_rating": 2,
                "lowest_rating": 1,
                "highest_rating": 3,
            },
        )

    def tearDown(self) -> None:

        main.cache = self.cache_copy

        del self.cache_copy
        del self.monkeypatch
        del self.client
        del self.app
