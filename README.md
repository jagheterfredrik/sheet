<p align="center">
  <img src="https://raw.githubusercontent.com/jagheterfredrik/sheet/master/sheet.png" alt="Sheet logo"/>
</p>
# Sheet
Sheet is an easy way of providing your user with a CLI API.

##Features
 - Authentication out of the box
 - No client-side installation
 - Everyone has the latest version, always

## Context
One of the most common ways to provide your customers with APIs today is to provide an HTTP API and to distribute a client-side script to talk to said API.

```
Database <-Connection A-> Business logic <-> HTTP API Server <-Connection B-> HTTP API Client
```

Deploy and done? No. It now turns out that your security professionals aren't happy because Connection B is running un-authenticated in the clear over your network.
Provide the HTTP API Server with an SSL certificate and done? No. We still don't have any way to authenticate the user.
Now what? Go ahead and build something to transfer an identity from the client to the server and somehow for the server to verify said identity.

What Sheet provides is a standards based (RFC4253) way of transferring the identity in a sane way to the server, the server still has to provide a way of verifying the identity by implementing an `AuthHandler` (there is a highly experimental LdapPubkeyAuthHandler included, ymmv).

## Usage
Sheet provides an easy way to host your API as an SSH Server, for which everyone already has a well-tested client, `ssh`. It currently comes preloaded with `shargh`, a wrapper around [argh](https://github.com/neithere/argh/).

Using the argh syntax, setup your commands and simply replace
```
argh.dispatch_commands([...])
```
with
```
shargh.serve_commands([...])
```

## Testing it out
```
virtualenv env
env/bin/pip install -r requirements.txt
env/bin/python test.py

ssh localhost -p 58337 -- --help
```

### Icon
Icon by by birdie brain at thenounproject.com