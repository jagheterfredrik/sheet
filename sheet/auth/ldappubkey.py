import paramiko
import ldap

from sheet.auth import base
from sheet.auth.broker import Broker

from sheet import util

@Broker.register
class LdapPubkeyAuthHandler(base.BaseAuthHandler):
    """Auth based on public keys stored in LDAP.

    Anonymously binds to LDAP in order to look up the public key for
    the connecting username and matches against the supplied key.
    """
    __id__ = 'LdapPubkeyAuth'
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
                ldapkey = entry.split(' ')
                if util.constant_time_compare(key.get_base64(), ldapkey[1]):
                    return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
