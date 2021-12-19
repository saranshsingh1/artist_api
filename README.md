### Please use the below instructions to run the assignment.

**Prerequisites**
1) `Python3` is required to run the assignment.
2) `Docker` setup is required to run MongoDB inside a container.
3) The assignment will work on a Mac or Linux machine.

#### Instructions to set up the project

1) Open a terminal (iTerm, Terminal, etc.)
2) Run MongoDB inside a docker container with the following command:
```docker
docker run --detach --name songs_db --publish 127.0.0.1:27017:27017 mongo:4.4
```

2) Once in the assignment folder, run `./run.sh`.
   1) This script creates a virtual environment if it doesn't exist,
   2) It installs the necessary dependencies, if needed,
   3) Activates the virtual environment,
   4) Imports the data into the MongoDB database.
   5) Starts the `gunicorn` WSGI server to run our application.

3) In the browser, go the link http://127.0.0.1:8005/songs.
4) To run the tests, open another terminal window and simply run `pytest`
if the virtual environment is activated else run `./run_tests.sh`.
5) Hit <kbd>&#8984;</kbd>/<kbd>CMD</kbd>+<kbd>C</kbd> key to stop the stop the server.
6) To add ratings for a given song, the fastest way is to use `cURL`
from the command line and send the data as a JSON object as demonstrated below
or use the `Postman` application if already present.
```shell
curl -X PUT -H "Content-Type: application/json" http://127.0.0.1:8005/ratings \
     -d '{"song_id":"use_id_from_browser_songs_endpoint","rating":"5"}'
```

**NOTE**: if the `run.sh` script does not work for some reason, please follow
the below steps as an alternative to above `step 2`.

1) Create a virtual environment with the command
```python
    python3 -m venv venv
```

2) Activate the virtual environment using the command
```python
    source venv/bin/activate
```
3) Install the dependencies using the command
```python
    pip install -r requirements.txt
```
4) Import the data into the MongoDB instance using the command
```python
    python import_data.py
```
5) Run the `gunicorn` server using the command
```python
    gunicorn main:app -b 127.0.0.1:8005
```
