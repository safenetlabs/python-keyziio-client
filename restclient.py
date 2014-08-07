# Keyzio REST API Client
# 
# Copyright (c) 2014 James FitzGerald. All rights reserved.
# 
# Note: calls are blocking (nothing asynchronous about this)
#
import logging
import json
import hashlib
import base64
import os
import requests
import requests.exceptions
import requests.auth
import traceback

class AuthFailure(Exception):
    """ Authentication attempt failed"""
    pass

class ServerFailure(Exception):
    """Connected to the server, but failed for some non-auth reason"""
    pass

class ConnectionFailure(Exception):
    """Not connected to the server at all """
    pass

class UnverifiedUser(Exception):
    """User authenticated successfully, however it seems their verification link has yet to be processed"""
    pass


# To handle requests exceptions, and re-raise as appropriate
class SmRestHandler():
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.info("Requests Exception: %s" % traceback.format_exc(exc_tb))
            if exc_type == requests.HTTPError:
                if exc_val.response.status_code == 422 or exc_val.response.status_code == 401:
                    raise AuthFailure
                elif exc_val.response.status_code == 404:
                    # Server returns 404 during onboarding if username/email is yet to be verified
                    raise UnverifiedUser
                else:
                    raise ServerFailure
            elif exc_type == requests.ConnectionError or exc_type == requests.Timeout:
                raise ConnectionFailure
            else:
                raise ConnectionFailure

class RestClient(object):
    """ Our Rest Client """

    USER_KEY_PATH = "user_keys.json"
    SESSIONS_PATH = "sessions.json"
    USERS_PATH = "users.json"

    def __init__(self, server_url="keyzio.herokuapp.com", server_port=80, use_ssl=False):
        # TODO: Enable SSL support and point to a hosted service

        self._server_url = server_url
        self._server_port = server_port
        self._use_ssl = use_ssl
        self.auth_data = None

        #logging.debug("ServerURL: " + samconfig.servername())
        # if samconfig.serverport():
        #     logging.debug("ServerPort: " + samconfig.serverport())
        # self._useSSL = samconfig.useSSL()
        # self._auth_token = None
        # if self._serverPort is None:
        #     self._serverPort = 443 if self._useSSL else 80
        self._session = None

    def _url(self, path):
        return "{scheme}://{server}:{port}/{api_path}".format(
            scheme='https' if self._use_ssl else 'http',
            server=self._server_url,
            port=self._server_port,
            api_path=path
        )

    def _api(self):
        if not self._session:
            self._session = requests.session()
            self._session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
                #,'Authorization': 'Bearer {0}'.format(self.auth_data['access_token'])

            default_user_agent = self._session.headers['User-Agent']
            self._session.headers['User-Agent'] = 'Keyzio Python Client'
            #self._session.verify = os.path.abspath(os.path.join(sampaths.resources_path(), 'cacerts.txt'))
        return self._session

    def _clear_auth_token(self):
        api = self._api()
        api.cookies.clear()
        if 'auth_token' in api.params:
            del api.params['auth_token']

    def set_oauth2_data(self, auth_data):
        self.auth_data = auth_data
        self._api().params['user_id'] = self.auth_data['id']
        self._api().params['access_token'] = self.auth_data['access_token']

    # def create_user(self, username, password):
    #     return self.post(self.USERS_PATH, {'email':username, 'password':password}).json()
    #
    # def authenticate(self, username, password):
    #     # Very basic authentication, other authentication mechanisms will be added
    #     if self.post(self.SESSIONS_PATH, {'email':username, 'password':password}).status_code != 200:
    #         raise AuthFailure

    def get_new_key(self, key_id):
        return self.post(self.USER_KEY_PATH, data={'identifier':key_id}).json()

    def get_key(self, key_id):
        if key_id:
            self._api().params['identifier'] = key_id
        else:
            self._api().params.pop("identifier", None)
        return self.get(self.USER_KEY_PATH).json()

    def put(self, path, data=None, **kwargs):
        return self.api_call('PUT', path, data, **kwargs)

    def get(self, path, **kwargs):
        return self.api_call('GET', path, **kwargs)

    def post(self, path, data=None, **kwargs):
        return self.api_call('POST', path, data, **kwargs)

    def delete(self, path, **kwargs):
        return self.api_call('DELETE', path, **kwargs)

    def api_call(self, method, path, data=None, etag=None, **kwargs):
        with SmRestHandler():
            data = json.dumps(data) if data else None
            if etag:
                headers = self._session.headers.copy()
                headers['If-None-Match'] = etag
            def doit(remaining_attempts):
                try:
                    return self._api().request(method, self._url(path), data=data, **kwargs)
                except requests.exceptions.SSLError as e:
                    if "handshake operation timed out" in str(e) and remaining_attempts > 0:
                        return doit(remaining_attempts - 1)
                    else:
                        raise e
            response = doit(5)
            response.raise_for_status()
            return response