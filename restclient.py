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
import traceback

NEW_KEY_PATH = "keyz/new"    # GET
GET_KEY_PATH = "keyz"         # GET

#define USERS_URL [NSString stringWithFormat:@"%@%@",SERVER,@"/users"]
#define USER_URL [NSString stringWithFormat:@"%@%@",SERVER,@"/user"]
#define USER_URL_AUTH(AUTH_TOKEN) [NSString stringWithFormat:(@"%@?auth_token=%@"),USER_URL,AUTH_TOKEN]

def password_digest(authSalt, password):
    pw_digest = base64.b64encode(hashlib.sha512(password + authSalt).digest())
    return pw_digest

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

    def __init__(self):
        self._serverURL = "localhost" #samconfig.servername()
        self._serverPort = 3000 #samconfig.serverport()
        self._useSSL = False
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
            scheme='https' if self._useSSL else 'http',
            server=self._serverURL,
            port=self._serverPort,
            api_path=path
        )

    def _api(self):
        if not self._session:
            self._session = requests.session()
            self._session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json',
                                          'Authorization': 'Bearer {0}'.format(self.auth_data['access_token'])})
            default_user_agent = self._session.headers['User-Agent']
            self._session.headers['User-Agent'] = 'Keyzio Python Client'
            #self._session.verify = os.path.abspath(os.path.join(sampaths.resources_path(), 'cacerts.txt'))
        return self._session

    def _clear_auth_token(self):
        api = self._api()
        api.cookies.clear()
        if 'auth_token' in api.params:
            del api.params['auth_token']

    def set_auth_data(self, auth_data):
        self.auth_data = auth_data
        self._api().params['user_id'] = self.auth_data['id']
        self._api().params['access_token'] = self.auth_data['access_token']

    def get_new_key(self, key_id):
        if key_id:
            self._api().params['identifier'] = key_id
        else:
            self._api().params.pop("identifier", None)


        return self.get(NEW_KEY_PATH).json()

    def get_key(self, key_id):
        return self.get('keyz/{}'.format(key_id)).json()



    #
    # def getUserData(self):
    #     """ User must have logged in already via login.  Returns the userBlob if the user has been onboarded,
    #     raises AuthFailure if the auth failed. connection failure if not connected at all, or ServerFailure if other response"""
    #     return self.get(USER_PATH).json()
    #
    # def uploadUserData(self, userData):
    #     """ upload the userData dictionary """
    #     return self.put(USER_PATH, data=userData)
    #
    # def uploadRecoveryPK(self, wrappedPK, keyId):
    #     """upload the recovery key and key id"""
    #     return self.post(RECOVERY_PATH, data={'key': wrappedPK, 'key_id': keyId}).json()
    #
    # def getRecoveryPKs(self):
    #     """upload the recovery key and key id"""
    #     return self.get(RECOVERY_PATH).json()
    #
    # def getResetKey(self):
    #     return self.get(RESET_KEY_PATH).json()
    #
    # def getIncomingShares(self):
    #     return self.get(INCOMING_SHARES_PATH).json()
    #
    # def getShares(self, etag=None):
    #     response = self.get(SHARES_PATH, etag=etag)
    #     # 304 is not modified
    #     if response.status_code == 304:
    #         return None, etag
    #     return (response.json(), None if 'etag' not in response.headers else str(response.headers['etag']))
    #
    # def getShare(self, share_id):
    #     return self.get("{}/{}".format(SHARES_PATH, share_id)).json()
    #
    # def getUser(self, user_id):
    #     return self.get("{}/{}".format(USERS_PATH, user_id)).json()
    #
    # def createUser(self, user_dict):
    #     return self.post(USERS_PATH, user_dict).json()
    #
    # def updateUser(self, user_id, user_dict):
    #     return self.put("{}/{}".format(USERS_PATH, user_id), user_dict).status_code
    #
    # def createShare(self, key_id):
    #     share = {
    #         "key_id": key_id,
    #         "key_type": "shek"
    #     }
    #     return self.post(SHARES_PATH, share).json()
    #
    # def updateShare(self, share_id, share_dict):
    #     return self.put("{}/{}".format(SHARES_PATH, share_id), share_dict).status_code
    #
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
    #
    # def _challengeResponse(self, password, challenge, authSalt):
    #     """ Doc on wiki is wrong.  Referencing David's code':
    #         //1. pw_concat = savedPassword + authSalt
    #         //2. pw_digest = (pw_concat sha512 (as bytes))base64
    #         //3. challenge_concat = pw_digest + challenge
    #         //4. response = ((challenge_concat) sha512)  base64 """
    #
    #     # My original version
    #     pw_digest = password_digest(authSalt, password)
    #     resp = base64.b64encode(hashlib.sha512(pw_digest + challenge).digest())
    #
    #     logging.debug("challenge response = %s" % resp)
    #     return resp
