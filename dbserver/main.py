""" Main Entry point.

NOTE
----
Return JSON Data:
    >>> headers = {'Content-Type': 'application/json'}
    >>> return make_response(json.dumps({'data': 'test'}) + '\n', 200, headers)

DataBase STRUCTURE:
    Group
        Label
            ClientData

"""

import hashlib
import json
import os

from typing import Optional, Any

import click

from flask import Flask, make_response, request
from flask_restful import Api, Resource

from click_logging import ClickLogger

from dbserver.database import Storage, StorageError


app = Flask(__name__)

app.config['dbauth'] = hashlib.sha256(os.getenv('DBAUTH').encode('utf-8')).hexdigest()
app.config['log_level'] = 'warning'

api = Api(app)


DataBase: Storage


# <<- Response handler for creating a valid server response
def json_response(code: int, error: Optional[str] = None, data: Optional[Any] = None,
                  bdata: Optional[bytes] = None, **header: Any) -> object:

    if bdata is not None:
        return make_response(
            bytes(bdata),
            int(code),
            {**{"Content-Type": "data/bytes"}, **header}
        )

    return make_response(
        json.dumps({
            "error": error,
            "data": data
        }), int(code),
        {**{"Content-Type": "application/json"}, **header}
    )
# ->>


# <<- Authentication decorator
def authenticate(func):
    def call(*args, **kwargs):
        if isinstance(request.authorization, dict):
            client_dbauth = "{}:{}".format(
                request.authorization['username'],
                request.authorization['password']
            )

            if hashlib.sha256(client_dbauth.encode()).hexdigest() == app.config['dbauth']:
                return func(*args, **kwargs)

        return json_response(401, "Authentication failed!")

    return call
# ->>


# <<- DataBase routes: '/db', '/db/<group>', '/db/<group>/<label>'
@api.resource('/db')
class DataBase(Resource):
    def __init__(self):
        super().__init__()
        self.log = ClickLogger(app.config['log_level'], 'route: /db')
        self.log.debug('__init__')

    @authenticate
    def get(self):
        """ List groups in database """
        self.log.debug("[GET]")

        response = DataBase.groups()

        return json_response(200, None, response)


@api.resource('/db/<group>')
class DataBaseGroup(Resource):
    def __init__(self):
        super().__init__()
        self.log = ClickLogger(app.config['log_level'], 'route: /db/<group>')
        self.log.debug('__init__')

    @authenticate
    def get(self, group):
        """ List 'Labels' in 'Group' """
        self.log.debug(f"[GET] ({group=})")

        try:
            response = DataBase.labels(group)

        except StorageError as ex:
            return json_response(ex.status, "Group not found!")

        return json_response(200, None, response)

    @authenticate
    def delete(self, group):
        """ Delete a 'Group' if empty """
        self.log.debug(f"[DELETE] ({group=})")

        try:
            DataBase.remove(group)

        except StorageError as ex:
            return json_response(ex.status, "Group no found!")

        return json_response(200)


@api.resource('/db/<group>/<label>')
class DataBaseLabel(Resource):
    def __init__(self):
        super().__init__()
        self.log = ClickLogger(app.config['log_level'], 'route: /db/<group>/<label>')
        self.log.debug('__init__')

    @authenticate
    def get(self, group, label):
        """ Get data for 'Label' in 'Group' """
        self.log.debug(f"[GET] ({group=}, {label=})")

        try:
            response = DataBase.get(group, label)

        except StorageError as ex:
            return json_response(ex.status, f"Label '{label}' not found in '{group}'!")

        return json_response(200, bdata=response)

    @authenticate
    def post(self, group, label):
        """ Create 'Label' with data if not already exists  """
        self.log.debug(f"[POST] ({group=}, {label=})")
        self.log.debug(f"[POST] {request.data=}")

        # check content type ('data/bytes')
        if request.headers.get('Content-Type') != 'data/bytes':
            return json_response(400, "Wrong content type specified!")

        if not request.data:
            return json_response(400, 'No data to store!')

        try:
            if label in DataBase.labels(group):
                return json_response(400, "Label already exists! (use PUT)")

        except StorageError:
            pass  # group not found

        try:
            DataBase.add(group, label, request.data)

        except StorageError as ex:
            return json_response(ex.status, 'Server Error!')

        return json_response(200)

    @authenticate
    def delete(self, group, label):
        """ Delete a 'Label' with data """
        self.log.debug(f"[DELETE] ({group=}, {label=})")

        try:
            DataBase.remove(group, label)

        except StorageError as ex:
            return json_response(ex.status, f"No such label: '{label}'!")

        return json_response(200)

    @authenticate
    def put(self, group, label):
        """ Overwrite existing 'Label' data """
        self.log.debug(f"[PUT] ({group=}, {label=})")

        # check content type ('data/bytes')
        if request.headers.get('Content-Type') != 'data/bytes':
            return json_response(400, "Wrong content type specified!")

        if not request.data:
            return json_response(400, 'No data to store!')

        try:
            if label not in DataBase.labels(group):
                return json_response(400, f"'{label}' not found! (use POST)")

        except StorageError:  # gorup not exists (use POST)
            return json_response(400, f"'{group}' not found! (use POST)")

        try:
            DataBase.add(group, label, request.data)

        except StorageError as ex:
            return json_response(ex.status, 'Server Error!')

        return json_response(200)
# ->>


# <<- cli : Entry Point
@click.command()
@click.option('--host', type=str, default='0.0.0.0')
@click.option('--port', type=int, default=50565)
@click.option('--log-level', type=click.Choice(ClickLogger.LEVELS), default=False)
@click.argument('database', type=click.Path(exists=True, file_okay=False, writable=True))
def cli(**kwargs):
    """ DBServer for storing data for network. """
    global DataBase

    app.config['log_level'] = kwargs['log_level']

    DataBase = Storage(kwargs['database'], kwargs['log_level'])

    cl = ClickLogger(kwargs['log_level'], 'Entry Point')
    cl.debug(f"{app.config}")
    cl.info(f"Run the flask server: 'http://{kwargs['host']}:{kwargs['port']}/'")

    app.run(
        debug=True if kwargs['log_level'] == 'debug' else False,
        host=kwargs['host'],
        port=kwargs['port']
    )
# ->>
