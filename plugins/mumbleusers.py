class Plugin():
	command = "#users"

	def __init__(self, mumble, irc):
		self.mumble = mumble
		self.irc = irc

	def __call__(self, sender, message, params=[]):
		self.users = []

		for x in self.mumble._userIds:

			if x.lower().find('bot') == -1:
				self.users += [x]

		return 'Currently ' + str(len(self.users)) + ' users connected to Mumble: '+', '.join(self.users) + ' | To download the client and connect, see http://mumble.thebutterzone.com'
