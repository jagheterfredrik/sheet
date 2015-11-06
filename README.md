<p align="center">
  <img src="https://raw.githubusercontent.com/jagheterfredrik/sheet/master/sheet.png" alt="Sheet logo"/>
</p>
# Sheet
Sheet is an easy way of providing your users with a CLI API.

## Features
 - No client-side installation
 - Identification out of the box
 - Encryption out of the box
 - Everyone has the latest version, always

## Context
One of the most common ways to provide your customers with APIs today is to provide an HTTP API and to distribute a client-side script to talk to said API:
```
Database <-Connection A-> Business logic + HTTP API Server <-Connection B-> HTTP API Client
```

Deploy and done? No. It now turns out that your security professionals aren't happy because Connection B is running un-authenticated in the clear over your network.

Provide the HTTP API Server with an SSL certificate and done? No. We still don't have any way to identify and authenticate the user.

Now what? Go ahead and build something to transfer an identity from the client to the server and somehow for the server to verify said identity.

What Sheet provides is a standards based (RFC4253) way of receiving an identity in a sane way from a regular SSH client:
```
Database <-Connection A-> Business logic + Sheet <-SSH Connection B-> ssh
```

However, the server still has to provide a way of verifying the identity. In Sheet this is done by implementing an `AuthHandler` (there is a highly experimental LdapPubkeyAuthHandler included, which will verify an SSH Public Key using an LDAP directory). Sheet currently includes two such AuthHandlers:
 - **BaseAuthHandler** disallows any public key, should'nt be used directly.
 - **PubkeyDirectoryAuthHandler** looks up the username as a filename in a specified filesystem directory and compares the public key within.
 - **LdapPubkeyAuthHandler** anonymously binds to LDAP, looks up the public key for the connecting username and matches against the supplied key.

## Usage
Sheet provides an easy way to host your API as an SSH Server, for which everyone already have a well-tested client, `ssh`.

The easiest way to make a CLI over SSH with Sheet is to use the included `shargh` module, a wrapper around [argh](https://github.com/neithere/argh/). Using the argh syntax, setup your commands and simply replace:
```python
import argh
...
argh.dispatch_commands([...])
```
with
```python
from sheet import shargh
...
shargh.serve_commands([...])
```

## Testing it out
```python
virtualenv env
env/bin/pip install -r requirements.txt
env/bin/python test.py

ssh test_client@localhost -i test_client.key -p 58337 -- work
```

By default it is setup to allow public keys in the `keys/` directory where the filename is the same as the authenticating username. Note that `keys/test_client` is the public part of `test_client.key`.

### Icon
Icon by by birdie brain at thenounproject.com
