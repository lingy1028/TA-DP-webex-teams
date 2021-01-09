import os
import sys
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
import splunklib.client as client

storage_passwords_logfile = os.sep.join([os.environ['SPLUNK_HOME'], 'var',
                       'log', 'splunk', 'webex_teams_storage_passwords.log'])
logging.basicConfig(filename=storage_passwords_logfile, level=logging.DEBUG)

# TODO 
"""
Only work for Python3
Doesn't work for Python2 in Splunk7.3 + Win2012
Modify it to make it work for Python2
"""

class SplunkStoragePasswords:
    """[summary]
    """
    def __init__(self, session_key, realm, app_name):
        """[summary]

        Args:
            session_key ([type]): [description]
            realm ([type]): [description]
            app_name ([type]): [description]
        """
        self.session_key = session_key
        self.realm = realm
        self.app_name = app_name
        self.storage_passwords = client.connect(token=session_key, app=app_name).storage_passwords
        

    def get(self, cred_name):
        """
        get cred from password storage endpoint
        """
        logging.debug("[*] getting" )
        try:
            returned_credential = [k for k in self.storage_passwords if k.content.get(
                'realm') == self.realm and k.content.get('username') == cred_name]
        except Exception as e:
            logging.info(
                "[*] Failed to get {}:{} from password storage. Error Message:  {}".format(self.realm, cred_name, repr(e)))
            raise e

        if len(returned_credential) == 0:
            logging.debug("[*] Doesn't exist")
            return None

        else:
            returned_credential = returned_credential[0]
            return returned_credential.content.get('clear_password')

    def delete(self, cred_name):
        """
        delete cred from password storage endpoint
        """
        logging.debug("[*] deleting...")
        if self.get(cred_name):
            try:
                self.storage_passwords.delete(cred_name, self.realm)
                logging.debug(
                    "[*] Deleted old {}:{}".format(self.realm, cred_name))
            except Exception as e:
                logging.info(
                    "[*] Failed to delete {}:{} from password storage. Error Message:  {}".format(self.realm, cred_name, repr(e)))
                raise e

    def update(self, cred_name, cred_password):
        """
        update cred from password storage endpoint
        """
        logging.debug("[*] updating...")
        self.delete(cred_name)
        # save it
        try:
            new_credential = self.storage_passwords.create(
                cred_password, cred_name, self.realm)
            logging.debug("[*] Updated {}:{}".format(self.realm, cred_name))
        except Exception as e:
            logging.info(
                "[*] Failed to update {}:{} from password storage. Error Message:  {}".format(self.realm, cred_name, repr(e)))
            raise e

