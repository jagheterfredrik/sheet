import paramiko
import sheet.auth.base

import ldap

class LdapPubkeyAuthHandler(sheet.auth.base.BaseAuthHandler):
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
