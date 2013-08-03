class Plugin():
	command = "#hello"

	def __init__(self, mumble, irc):
		self.mumble = mumble
		self.irc = irc
	
	def __call__(self, sender, message, params=[]):
		return "Hello, %s" % (sender,)
