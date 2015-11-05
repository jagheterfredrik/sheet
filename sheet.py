#!/usr/bin/env python
from binascii import hexlify
import socket
import sys
import traceback
import paramiko
import threading
import ldap
import base64

# setup logging
paramiko.util.log_to_file('demo_server.log')

host_key = paramiko.RSAKey(filename='test_rsa.key')

class BaseAuthHandler(paramiko.ServerInterface):
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
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'publickey'

class LdapPubkeyAuthHandler(BaseAuthHandler):
    def __init__(self, host, port, base_dn, username_field, pubkey_field):
        super(LdapPubkeyAuthHandler, self).__init__()
        self.host = host
        self.port = port
        self.base_dn = base_dn
        self.username_field = username_field
        self.pubkey_field = pubkey_field
        self.ldap = ldap.initialize(self.host)
        self.ldap.simple_bind()

    def check_auth_publickey(self, username, key):
        uid, res = self.ldap.search_s(self.base_dn, ldap.SCOPE_SUBTREE, self.username_field+'='+username)[0]
        if self.pubkey_field in res:
            for entry in res[self.pubkey_field]:
                keytype, ldapkey, email = entry.split(' ', 3)
                if key.get_base64() == ldapkey:
                    return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

class Server():
    def __init__(self, cb, address='', port=58337, backlog=100):
        #super(Server, self).__init__(name='SheetServer')
        self.cb = cb
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((address, port))
        except Exception as e:
            print 'Bind failed: ', str(e)
            traceback.print_exc()
            sys.exit(1)

        try:
            #TODO backlog
            self.socket.listen(backlog)
            print 'Listening for connection ...'
        except Exception as e:
            print 'Listen/accept failed:', str(e)
            traceback.print_exc()
            sys.exit(1)

    def start(self):
        while True:
            try:
                client, addr = self.socket.accept()
                ServerThread(client, addr, self.cb).start()
            except KeyboardInterrupt:
                print 'Shutting down!'
                self.socket.close()
                break

class ServerThread(threading.Thread):
    def __init__(self, client, addr, cb):
        super(ServerThread, self).__init__(name='SheetServerThread')
        self.client = client
        self.addr = addr
        self.cb = cb

    def run(self):
        t = paramiko.Transport(self.client, gss_kex=False)
        t.add_server_key(host_key)
        #handler = LdapPubkeyAuthHandler('ldap://ldap-ash2.spotify.net', 389, 'cn=users,dc=carmen,dc=int,dc=sto,dc=spotify,dc=net', 'uid', 'sshPublicKey')
        handler = BaseAuthHandler()
        try:
            t.start_server(server=handler)
        except paramiko.SSHException:
            return

        chan = t.accept(10)
        if chan is None:
            return

        infile = chan.makefile('r')
        outfile = chan.makefile('w')
        errfile = chan.makefile_stderr('w')

        status = self.cb(handler.command, infile, outfile, errfile)

        chan.send_exit_status(status)
        chan.shutdown(2)
        chan.close()
        t.close()
