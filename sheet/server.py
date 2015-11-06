import socket
import sys
import traceback
import paramiko
import threading
import yaml

from paramiko.rsakey import RSAKey

from sheet.auth.broker import Broker
from sheet.auth import *

class Server():
    def __init__(self, cb, config=None, address='', port=58337, backlog=100):
        self.cb = cb

        # Parse config <3
        if config is not None:
            with open(config, 'r') as f:
                cfg = yaml.load(f)
        else:
            cfg = {}

        logfile = cfg.get('logfile', None)
        if logfile is not None:
            paramiko.util.log_to_file(logile)

        host_key_path = cfg.get('host_key', 'server.key')
        host_key_password = cfg.get('host_key_password', None)
        try:
            self.host_key = RSAKey.from_private_key_file(host_key_path, host_key_password)
        except paramiko.ssh_exception.PasswordRequiredException:
            print 'Invalid host_key_password'
            sys.exit(1)
        except IOError:
            print '*****************************************'
            print '**      host_key does not exists!      **'
            print '** In the name of security by default, **'
            print '**   Sheet will generate one for you.  **'
            print '*****************************************'
            RSAKey.generate(2048).write_private_key_file(host_key_path, host_key_password)

        self.handler = Broker.get(cfg.get('auth_handler', 'BaseAuth'))
        self.handler_conf = cfg.get('auth_handler_config', {})

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((address, port))
        except Exception as e:
            print 'Bind failed: ', str(e)
            traceback.print_exc()
            sys.exit(1)

        try:
            self.socket.listen(backlog)
        except Exception as e:
            print 'Listen/accept failed:', str(e)
            traceback.print_exc()
            sys.exit(1)

    def start(self):
        while True:
            try:
                client, addr = self.socket.accept()
                ServerThread(client, addr, self.cb, self.host_key, self.handler, self.handler_conf).start()
            except KeyboardInterrupt:
                self.socket.close()
                break

class ServerThread(threading.Thread):
    def __init__(self, client, addr, cb, host_key, handler, handler_conf):
        super(ServerThread, self).__init__(name='SheetServerThread')
        self.client = client
        self.addr = addr
        self.cb = cb
        self.host_key = host_key
        self.handler = handler
        self.handler_conf = handler_conf

    def run(self):
        t = paramiko.Transport(self.client, gss_kex=False)
        t.add_server_key(self.host_key)
        #handler = LdapPubkeyAuthHandler()
        handler = self.handler(**self.handler_conf)
        try:
            t.start_server(server=handler)
        except paramiko.SSHException:
            return
        except EOFError:
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
