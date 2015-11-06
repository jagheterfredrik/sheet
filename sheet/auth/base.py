import paramiko

from sheet.auth.broker import Broker

@Broker.register
class BaseAuthHandler(paramiko.ServerInterface):
    "Provides base class for authentication, never use directly."

    __id__ = 'BaseAuth'

    def __init__(self):
        self.command = None

    def check_channel_request(self, kind, channel):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_exec_request(self, channel, command):
        self.command = command
        return True

    def check_auth_publickey(self, username, key):
        if False:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'publickey'
