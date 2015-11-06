class AuthBroker(object):
	def __init__(self):
		self.providers = {}

	def register(self, classdef):
		name = classdef.__id__
		if name in self.providers:
			print 'Provider', name, 'defined more than once'
		self.providers[name] = classdef
		return classdef

	def get(self, name):
		if not name in self.providers:
			print 'The configured provider does not exist'
		return self.providers[name]

Broker = AuthBroker()
