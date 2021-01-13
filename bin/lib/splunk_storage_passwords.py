import os
import sys
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
import splunklib.client as client

class SplunkStoragePasswords(object):
    """
    Used to Retrun a SplunkStoragePasswords object which contains 
    collection of the storage passwords on this Splunk instance.
    """
    def __init__(self, session_key, realm, app_name):
        """
        Args:
            session_key (string): The current session token
            realm (string): The credential realm
            app_name (string): The TA's name
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
            logging.error(
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
                logging.error(
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
            logging.error(
                "[*] Failed to update {}:{} from password storage. Error Message:  {}".format(self.realm, cred_name, repr(e)))
            raise e

