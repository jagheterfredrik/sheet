import socket
import sys
import traceback
import paramiko
import threading

import sheet.auth.base

# setup logging
paramiko.util.log_to_file('demo_server.log')

host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server():
    def __init__(self, cb, address='', port=58337, backlog=100, handler=sheet.auth.base.BaseAuthHandler):
        #super(Server, self).__init__(name='SheetServer')
        self.cb = cb
        self.handler = handler
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
                ServerThread(client, addr, self.cb, self.handler).start()
            except KeyboardInterrupt:
                print 'Shutting down!'
                self.socket.close()
                break

class ServerThread(threading.Thread):
    def __init__(self, client, addr, cb, handler):
        super(ServerThread, self).__init__(name='SheetServerThread')
        self.client = client
        self.addr = addr
        self.cb = cb
        self.handler = handler

    def run(self):
        t = paramiko.Transport(self.client, gss_kex=False)
        t.add_server_key(host_key)
        #handler = LdapPubkeyAuthHandler('ldap://ldap-ash2.spotify.net', 389, 'cn=users,dc=carmen,dc=int,dc=sto,dc=spotify,dc=net', 'uid', 'sshPublicKey')
        handler = self.handler()
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
