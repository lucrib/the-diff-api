# Diff REST API
This is a simple rest api developed over flask that receives base64 encoded data through JSON and 
generate the diff between them.

# Deploy
In order to have the service up and running you have to:
    1. Install virtual env to you environment. Take a look [here](https://virtualenv.pypa.io/en/stable/).
    2. Clone this repo: `git clone https://github.com/lucrib/waes-assignment.git`
    3. Move to the folder: `cd waes-assigngment`
    4. Create virtualenv: `virtualenv venv`
    5. Activate the virtualenv: `source venv/bin/activate`
    6. Download the dependencies: `pip install -r requirements.txt`
    7. Create the database: `python db_create.py`
    8. Start the service: `python run.py`

# Usage
There are 3 endpoints available:
1.  `http://host/v1/diff/<id>/left` - Receives data to be diff-ed
2.  `http://host/v1/diff/<id>/right` - Receives data to be diff-ed on the other side
3.  `http://host/v1/diff/<id>` - Compares the data under the same `id` and answer back the offset and length of the diff

## Sending the data to be diff-ed
The left and right side expects to receive a JSON object through `POST` method as follows:
```json
{
    "data": "VEVTVEVfREFUQQ=="
}
```

Example:
`curl -i -X POST http://hortname/v1/1/left -H "Content-Type: application/json" -d '{"data": "VEVTVEVfREFUQQ=="}'`
_Notice: The id is informed in the url only, if the id is already in use the server will answer with 409 and a JSON message_

The answer will be a JSON:
```json
{
    "id": 1
    "side": "left",
    "uri": "http://hostname/v1/1/left"
}
```

This endpoint also accepts 3 other methods:
    * `GET` - Return the information of the diff side if there is information.
    * `PUT` - Receives the same JSON of the `POST` method but will update the data.
    * `DELETE` - Deletes the data.

## Getting the diff of data
In order to get the diff-ed data, the left and right data must have been sent previously.
_Example:_
`curl `
This will answer with a JSON like this:
```json
{
    "uri": "http://localhost/v1/diff/1",
    "id": 1,
    "result": {
        "message": "Offset: 0, Length: 6\nOffset: 18, Length: 3\n",
        "code": 1
    }
}
```
_Notice: If there are more than one difference in the comparison this will come inside `"message"` too._
