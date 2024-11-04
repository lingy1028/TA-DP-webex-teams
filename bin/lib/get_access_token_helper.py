import time as mytime
import requests
import sys
import json
import os
import requests
from lib.splunk_storage_passwords import SplunkStoragePasswords 

SPLUNK_DEST_APP = 'TA-DP-webex-teams'
APP_NAME = 'TA-DP-webex-teams'
REALM = 'TA-DP-webex-teams-oauth-creds'
TOKENS_KEY = "oauth_tokens"
DELTA_TIME = 2*24*60*60 # 48 hours
ACCESS_TOKEN_EXPIRATION_TIME_NAME = "access_token_expiration_time_name"


def update_access_token(helper, client_id, client_secret, refresh_token):
    """
    Get access token using refresh token
    """

    url = "https://api.ciscospark.com/v1/access_token"

    payload = {'grant_type': 'refresh_token',
               'client_id': client_id,
               'client_secret': client_secret,
               'refresh_token': refresh_token
               }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        helper.log_debug(
            "[-] GET Access Token from Refresh Token: response.status_code: {}".format(response.status_code))
        if response.status_code != 200:
            helper.log_info(
                "\t[-] Error happend to get Access Token from Refresh Token: {}".format(response.text))
        else:
            resp = response.json()
            if resp.get('access_token'):
                access_token = resp['access_token']
                refresh_token = resp['refresh_token']
                expires_in = resp['expires_in']

                # update storage/passwords and checkpoint
                update_storage_passwords_checkpoint(helper, access_token, refresh_token, expires_in)

                return access_token, refresh_token, expires_in
    except Exception as e:
        helper.log_error(
            "[-] Webex Teams request failed to get Access Token from Refresh Token: {}".format(repr(e)))
        raise e

def update_storage_passwords_checkpoint(helper, access_token, refresh_token, expires_in):
    # create a splunk_storage_passwords object
    session_key = helper.context_meta['session_key']
    my_splunk_storage_passwords = SplunkStoragePasswords(session_key, REALM, APP_NAME)

    # update new tokens data in password storage
    try:
        tokens_data = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_in": expires_in
                        }

        my_splunk_storage_passwords.update(TOKENS_KEY, json.dumps(tokens_data))
        helper.log_debug("\t[-] Saved tokens into storage/password endpoint")
    except Exception as e:
        helper.log_error("[-] Failed to save Access Token and Refresh Token to storage/password endpoint. : {}".format(repr(e)))
        raise e

    # update access_token_expiration_time checkpoint
    try:
        now = int(mytime.time())
        new_access_token_expiration_time =  now + expires_in - DELTA_TIME

        helper.log_debug("\t[-] now: {}".format(now))
        helper.log_debug("\t[-] new_access_token_expires_in: {}".format(expires_in))
        helper.log_debug("\t[-] new_access_token_expiration_time: {}".format(new_access_token_expiration_time))
        helper.log_info("\t[-] Storing news access_token_expiration_time")
        helper.save_check_point(ACCESS_TOKEN_EXPIRATION_TIME_NAME, new_access_token_expiration_time)
    except Exception as e:
        helper.log_error("[-] Failed to save access_token_expiration_time checkpoint : {}".format(repr(e)))
        raise e

def get_access_token(helper, client_id, client_secret):
    # create a splunk_storage_passwords object
    session_key = helper.context_meta['session_key']
    my_splunk_storage_passwords = SplunkStoragePasswords(session_key, REALM, APP_NAME)
    helper.log_debug('[-] splunk_storage_passwords: {}'.format(type(my_splunk_storage_passwords)))

    # Get the tokens data from storage/password endpoint
    try:
        helper.log_debug("[-] Getting data from storage/password endpoint ...")
        tokens_data = my_splunk_storage_passwords.get(TOKENS_KEY)
        tokens_data = json.loads(tokens_data)
        access_token = tokens_data.get("access_token", None)
        refresh_token = tokens_data.get("refresh_token", None)
        access_token_expires_in = tokens_data.get("expires_in", None)

        helper.log_debug("[-] access_token: {}".format(access_token))
        helper.log_debug("[-] refresh_token: {}".format(refresh_token))
        helper.log_debug("[-] access_token_expires_in: {}".format(access_token_expires_in))
    except Exception as e:
        helper.log_error(
            "[-] Failed to get Access Token and Refresh Token from storage/password endpoint. You might need to re-configure the TA to re-get the tokens!: {}".format(repr(e)))
        raise e

    # Access Token Management
    # get the access_token_expiration_time checkpoint
    access_token_expiration_time =  helper.get_check_point(ACCESS_TOKEN_EXPIRATION_TIME_NAME)

    # Used for access token expiry
    current_run_epoch = int(mytime.time())
    
    # First time 
    if access_token_expiration_time is None:
        access_token_expiration_time = current_run_epoch + access_token_expires_in - DELTA_TIME # Set it to be 24 hours before the actual expiry
        helper.log_info("[-] Storing news access_token_expiration_time")
        helper.log_debug("[-] access_token_expiration_time: {}".format(access_token_expiration_time))
        helper.save_check_point(ACCESS_TOKEN_EXPIRATION_TIME_NAME, access_token_expiration_time)
    helper.log_debug("[-] current_run_epoch: {}".format(current_run_epoch))
    helper.log_debug("[-] access_token_expires_in: {}".format(access_token_expires_in))
    helper.log_debug("[-] access_token_expiration_time: {}".format(access_token_expiration_time))

    # Check if current access token is expired 
    helper.log_debug("[-] access_token_expiration_time <=? current_run_epoch -- {} <=? {} ".format(access_token_expiration_time, current_run_epoch))
    if access_token_expiration_time<=current_run_epoch:
        # update access_token
        helper.log_info("[-] Current access_token is EXPIRED")
        new_access_token, new_refresh_token, new_access_token_expires_in = update_access_token(helper, client_id, client_secret, refresh_token)
        return new_access_token, new_refresh_token
    else:
        helper.log_info("[-] Current access_token still valid.")
        return access_token, refresh_token
