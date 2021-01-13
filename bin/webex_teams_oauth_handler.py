from splunk.persistconn.application import PersistentServerConnectionApplication
import os
import sys
import json
import logging
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
# import splunklib.client as client
from splunk_storage_passwords import SplunkStoragePasswords 

SPLUNK_DEST_APP = 'TA-DP-webex-teams'


if sys.platform == "win32":
    import msvcrt
    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

logfile = os.sep.join([os.environ['SPLUNK_HOME'], 'var',
                       'log', 'splunk', 'webex_teams_oauth_handler.log'])
logging.basicConfig(filename=logfile, level=logging.DEBUG)


def flatten_query_params(params):
    # Query parameters are provided as a list of pairs and can be repeated, e.g.:
    #
    #   "query": [ ["arg1","val1"], ["arg2", "val2"], ["arg1", val2"] ]
    #
    # This function simply accepts only the first parameter and discards duplicates and is not intended to provide an
    # example of advanced argument handling.
    flattened = {}
    for i, j in params:
        flattened[i] = flattened.get(i) or j
    return flattened

class WebexTeamsOauthHandler(PersistentServerConnectionApplication):
    def __init__(self, _command_line, _command_arg):
        super(PersistentServerConnectionApplication, self).__init__()

    # Handle a syncronous from splunkd.
    def handle(self, in_string):
        """
        Called for a simple synchronous request.
        @param in_string: request data passed in
        @rtype: string or dict
        @return: String to return in response.  If a dict was passed in,
                 it will automatically be JSON encoded before being returned.
        """

        request = json.loads(in_string)
        logging.debug('type of request: {}'.format(type(request)))

        method = request['method']
        logging.debug('method: {}'.format(method))

        # get session_key
        session_key = request['session']['authtoken']
        
        # define required params
        app_name = 'TA-DP-webex-teams'
        realm = 'TA-DP-webex-teams-oauth-creds'
        creds_key = "oauth-creds"

        # create splunkService
        # splunkService = client.connect(token=session_key, app=SPLUNK_DEST_APP)

        # create a splunk_storage_passwords object
        my_splunk_storage_passwords = SplunkStoragePasswords(session_key, realm, app_name)
        logging.info('splunk_storage_passwords: {}'.format(type(my_splunk_storage_passwords)))

        if method == "POST":
            logging.debug('[-] Handling POST request from UI')
            try:
                form_params = flatten_query_params(request['form'])
                logging.debug(
                    'type of form_params: {}'.format(type(form_params)))
              
                redirect_uri = form_params.get("redirect_uri", None)
                client_id = form_params.get("client_id", None)
                client_secret = form_params.get(
                    "client_secret", None)

                creds_data = {
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }

                # save creds data into storage/password endpoint
                my_splunk_storage_passwords.update(creds_key, json.dumps(creds_data))            
                logging.debug("[-] Saved creds data into storage/password endpoint")

            except Exception as e:
                logging.error("err: {}".format(e))
                pass
            return {'payload': request, 'status': 200}
        elif method == "GET":
            logging.debug('[-] Handling GET request from Webex Teams Server')

            # Get the creds from storage/password endpoint
            logging.debug("[-] Getting data from storage/password endpoint ...")
            creds_dict = my_splunk_storage_passwords.get(creds_key)

            if creds_dict:
                try:
                    creds_dict = json.loads(creds_dict)
                    redirect_uri = creds_dict.get("redirect_uri", None)
                    client_id = creds_dict.get("client_id", None)
                    client_secret = creds_dict.get(
                        "client_secret", None)

                    # get the code from request query params
                    query_params = flatten_query_params(request['query'])
                    code = query_params['code']
                    # logging.debug("code: {}".format(code))

                    # send POST request to the Webex Teams Server
                    url = "https://webexapis.com/v1/access_token"

                    payload = {'grant_type': 'authorization_code',
                               'client_id': client_id,
                               'client_secret': client_secret,
                               'code': code,
                               'redirect_uri': redirect_uri
                               }
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }

                    response = requests.request(
                        "POST", url, headers=headers, data=payload)

                    logging.debug(
                        "response code -- {}".format(response.status_code))

                    status_code = response.status_code
                    resp = response.json()

                    if status_code != 200:
                        return {'payload': response.text, 'status': 200}

                    if resp['access_token'] and resp['refresh_token']:

                        logging.debug('[-] Saving Tokens into storage/password endpoint')
                    
                        tokens_key = "oauth_tokens"
                        tokens_data = {
                            "access_token": resp['access_token'],
                            "refresh_token": resp['refresh_token'],
                            "expires_in": resp['expires_in']                          
                        }

                        # save tokens into storage/password endpoint
                        my_splunk_storage_passwords.update(tokens_key, json.dumps(tokens_data))            
                        logging.debug("[-] Saved tokens into storage/password endpoint")
                        
                        # Return information to UI
                        result = '''
                        <div style='width:510px;'>
                            <h1>Permissions Granted!</h1>
                        </div>
                        <div style='word-break: break-all;'>
                            <h3>Successfully Saved Access Token and Refresh Token!</h3>
                            <h3>Please CLOSE This Page!</h3>
                            <br>
                            <h4>Access Token</h4>
                            <p>{access_token}</p>
                            <br>
                            <h4>Refresh Token</h4>
                            <p>{refresh_token}</p>
                        </div>
                        ''' .format(access_token=resp['access_token'], refresh_token=resp['refresh_token'])

                except Exception as e:
                    logging.error("Payload error: {}".format(e))
                
                return {'payload': result, 'status': 200}
                
               
    def handleStream(self, in_string):
        """
        For future use
        """
        raise NotImplementedError(
            "PersistentServerConnectionApplication.handleStream")

    def done(self):
        """
        Virtual method which can be optionally overridden to receive a
        callback after the request completes.
        """
        pass
