__author__ = 'James FitzGerald'
__version__ = '0.1'

#import oauth2
import urlparse
import sanction
import urllib, urllib2
import shutil
from StringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import logging
import json
import threading

log = logging.getLogger(__name__)

# I will return this from the authenticate call
auth_data = None


# Facebook
# APP_ID = '582939211817604'
# APP_SECRET = '999b56c8c75fcf1519250f793c539c16'

# Github
APP_ID =  'af3380d5289b6ff021b8'
APP_SECRET = '29a5fcb7214f22e0075df7a9c54464228e4bb796'
# http://localhost:3000/oauth_callback

LOCAL_CALLBACK_URI = "http://localhost:3001/oauth_callback"
AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
RESOURCE_URL = "https://github.com/james-fitzgerald"

USER_API_URL = "https://api.github.com/user"

c = sanction.Client(auth_endpoint=AUTHORIZE_URL, token_endpoint=TOKEN_URL, resource_endpoint=RESOURCE_URL,
                    client_id=APP_ID, client_secret=APP_SECRET)

class SampleAppHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = 'SampleAppHTTPRequestHandler/%s' % __version__

    def _serve_msg(self, code, msg):
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<body>\n%s</body>\n</html>\n" % msg)
        length = f.tell()
        f.seek(0)

        if code == 200:
            self.send_response(code)
        else:
            self.send_error(code, message=msg)

        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(length))
        self.end_headers()

        shutil.copyfileobj(f, self.wfile)

    def _bad_request(self):
        """Serve Bad Request (400)."""
        self._serve_msg(400, 'Bad Request')

    def prepare_request(self):
        request_data = {}
        request_data['server_name'] = self.server.server_name
        request_data['server_port'] = str(self.server.server_port)
        request_data['path_info'] = self.path
        request_data['request_uri'] = self.path
        request_data['script_name'] = ''
        if self.protocol_version == 'HTTP/1.0':
            request_data['https'] = 'off'
        else:
            request_data['https'] = 'on'
        return request_data

    def log_message(self, format, *args):
        log.info(format % args)

    def do_HEAD(self):
        """Serve a HEAD request."""
        self._bad_request()

    def do_DEL(self):
        """Serve a DEL request."""
        self._bad_request()

    def do_GET(self):
        """Serve a GET request."""

        if "oauth_callback" in self.path:
            self.handle_oauth_callback()
        else:
            self._bad_request()
            #self._serve_msg(200, "All good mate!")
        # if not self.path == '/':
        #     self._bad_request()
        #     return
        #
        # url = AuthRequest.create(**self.settings)
        # self.send_response(302)
        # self.send_header("Cache-Control", "no-cache, no-store")
        # self.send_header("Pragma", "no-cache")
        # self.send_header("Location", url)
        # self.end_headers()

    def do_POST(self):
        """Serve a POST request."""
        if not self.path == self.saml_post_path:
            self._bad_request()
            return
        request_data = self.prepare_request()
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        query = urlparse.parse_qs(data)


    def handle_oauth_callback(self):
        # TODO: extract state and compare to our state
        # extract code
        parts = urlparse.urlparse(self.path)
        query = urlparse.parse_qs(parts.query)

        print self.headers

        # Convert code to an access token
        code = query['code'][0]
        c.request_token(code=code)

        # Now retrieve user info
        user_uri = '{}?{}'.format(USER_API_URL, urllib.urlencode({'access_token':c.access_token}))

        msg = urllib2.urlopen(user_uri)
        data = json.loads(msg.read().decode(msg.info().get_content_charset() or 'utf-8'))

        self._serve_msg(200, "All good mate!  Access token is {}\n User is {} \n id is {}".format(c.access_token,
                                                                                                  data['login'],
                                                                                                  data['id']))

        # Authentication result
        global auth_data
        auth_data = data
        auth_data['access_token'] = c.access_token

        # kill our server, our job is done
        threading.Thread(target=lambda: httpd.shutdown()).start()

def open_browser(auth_uri):
    import webbrowser
    webbrowser.open_new(auth_uri)

def launch_browser_to_authenticate(auth_uri):
    threading.Thread(target=lambda:open_browser(auth_uri)).start()

def authenticate():

    auth_uri = c.auth_uri(redirect_uri=LOCAL_CALLBACK_URI, state="aaaaaaaaaaaa", scope="user,repo,gist")

    #parts = urlparse.urlparse(settings['assertion_consumer_service_url'])
    SampleAppHTTPRequestHandler.protocol_version = 'HTTP/1.0'
    #SampleAppHTTPRequestHandler.settings = settings
    #SampleAppHTTPRequestHandler.saml_post_path = parts.path
    # httpd = HTTPServer(
    #     ("localhost", 3001),
    #     SampleAppHTTPRequestHandler,
    # )

    socket_name = httpd.socket.getsockname()

    log.info(
        'Serving HTTP on {host} port {port} ...'.format(
            host=socket_name[0],
            port=socket_name[1],
        )
    )

    launch_browser_to_authenticate(auth_uri)
    httpd.serve_forever()
    return auth_data

    # request_token_url = "http://facebook.com/oauth/request_token"
    # access_token_url = 'http://facebook.com/oauth/access_token'
    # authorize_url = 'https://github.com/oauth/authorize'
    #
    # # Step 1: Get a request token. This is a temporary token that is used for
    # # having the user authorize an access token and to sign the request to obtain
    # # said access token.
    #
    # resp, content = client.request(request_token_url, "GET")
    # print resp
    # print content
    #
    # if resp['status'] != '200':
    #     raise Exception("Invalid response %s." % resp['status'])
    #
    # request_token = dict(urlparse.parse_qsl(content))
    #
    # print "Request Token:"
    # print "    - oauth_token        = %s" % request_token['oauth_token']
    # print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    # print
    #
    # # ** -- JF: Here I will start a local server and launch the browser or embedded WebView **
    # # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # # redirect. In a web application you would redirect the user to the URL
    # # below.
    #
    # print "Go to the following link in your browser:"
    # print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    # print
    #
    # # After the user has granted access to you, the consumer, the provider will
    # # redirect you to whatever URL you have told them to redirect to. You can
    # # usually define this in the oauth_callback argument as well.
    # accepted = 'n'
    # while accepted.lower() == 'n':
    #     accepted = raw_input('Have you authorized me? (y/n) ')
    # oauth_verifier = raw_input('What is the PIN? ')
    #
    # # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # # URL you can request the access token the user has approved. You use the
    # # request token to sign this request. After this is done you throw away the
    # # request token and use the access token returned. You should store this
    # # access token somewhere safe, like a database, for future use.
    # token = oauth2.Token(request_token['oauth_token'],
    #     request_token['oauth_token_secret'])
    # token.set_verifier(oauth_verifier)
    # client = oauth2.Client(consumer, token)
    #
    # resp, content = client.request(access_token_url, "POST")
    # access_token = dict(urlparse.parse_qsl(content))
    #
    # print "Access Token:"
    # print "    - oauth_token        = %s" % access_token['oauth_token']
    # print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    # print
    # print "You may now access protected resources using the access tokens above."
    # print


httpd = HTTPServer(("localhost", 3001), SampleAppHTTPRequestHandler,)


def main():
    print authenticate()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print e
    print "finished"

