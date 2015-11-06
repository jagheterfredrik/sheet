import paramiko
from os.path import isfile, normpath, join

from sheet.auth import base
from sheet.auth.broker import Broker
from sheet import util

@Broker.register
class PubkeyDirectoryAuthHandler(base.BaseAuthHandler):
    """Allows public keys in a specified filesystem directory where
    the filename matches the username.
    """

    __id__ = 'PubkeyDirectoryAuth'

    def __init__(self, path):
        super(PubkeyDirectoryAuthHandler, self).__init__()
        self.path = path

    def check_auth_publickey(self, username, key):
        sanitized_username = normpath('/' + username).lstrip('/')
        keypath = join(self.path, sanitized_username)
        if isfile(keypath):
            with open(keypath, 'r') as f:
                filekey = f.read().split(' ')
                if util.constant_time_compare(key.get_base64(), filekey[1]):
                    return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
