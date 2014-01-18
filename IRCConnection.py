import AbstractConnection
import sys
import socket
import string
import re

class IRCConnection(AbstractConnection.AbstractConnection):

	# call the superconstructor and set global configuration variables.
	def __init__(self, hostname, port, nickname, password, channel, encoding, name, loglevel):
		super(IRCConnection,self).__init__(name, loglevel)
		self._hostname = hostname
		self._port = port
		self._nickname = nickname
		self._password = password
		self._channel = channel
		self._encoding = encoding
		# the socket that will be used for communication with the IRC server:
		self._socket = None

	# open the socket and return true. don't catch exceptions, since the run() wrapper will do that.
	def _openConnection(self):
		self._socket = socket.socket()
		self._socket.connect((self._hostname, self._port))
		return True

    # compile the regex used in SendTextMessageUnsafe function below
	_endloesung = re.compile("<(/)?[^>]*>")

    # open the socket and return true. don't catch exceptions, since the run() wrapper will do that.
	def _openConnection(self):
		self._socket = socket.socket()
		self._socket.connect((self._hostname, self._port))
		return True

	# send initial packages (PASSword, NICKname, USER identification, channel JOIN).
	def _initConnection(self):
		if not self._sendMessage("PASS %s" % self._password):
			raise Exception("could not send PASS message.")
		if not self._sendMessage("NICK %s" % self._nickname):
			raise Exception("could not send NICK message.")
		if not self._sendMessage("USER %s %s bla :%s" % (self._nickname, self._hostname, self._nickname)):
			raise Exception("could not send USER message.")
		if not self._sendMessage("JOIN #%s" % self._channel):
			raise Exception("could not send JOIN message.")
		return True

	# post-connect, call _connectionEstablished() and return true.
	def _postConnect(self):
		return True

	# close the socket.
	def _closeConnection(self):
		self._sendMessage("QUIT");
		self._socket.shutdown(socket.SHUT_RDWR)
		self._socket.close()
		return True

	# the read buffer, which contains all currently read, but uninterpreted data.
	_readBuffer = ""

	# read and interpret data from socket in this method.
	def _listen(self):
		# read up to 4 kB of data into the buffer.
		self._readBuffer += self._socket.recv(4096)
		# get all distinct lines from the buffer into lines.
		lines = self._readBuffer.split('\n')
		# move the last (unfinished) line back into the buffer.
		self._readBuffer = lines.pop()

		# process all lines.
		for line in lines:
			try:
				iline = line.decode(self._encoding, errors='ignore')
			except:
				self._log("received a line which is not valid " + self._encoding + ": " + repr(iline), 1)
			line = iline
			self._log("rx: "+line, 3)
			# split the line up at spaces
			line = line.rstrip().split(' ', 3)

			# check if the line contains a ping message (PING)
			if(len(line) >= 2):
				if(line[0] == "PING"):
					self._sendMessage("PONG " + line[1])

			# check if the line contains a private message (PRIVMSG)
			if(len(line) >= 4):
				if(line[1] == "PRIVMSG"):
					self._invokeTextCallback(line[0].split('!')[0].lstrip(': '), line[3].lstrip(': '))
				if(line[3] == "#" + self._channel + " :End of /NAMES list."):
					self._connectionEstablished();

		return True



	# pass the given line to _sendMessage, encoded as a PRIVMSG to #self._channel.
	def _sendTextMessageUnsafe(self, message):
		return self._sendMessage("PRIVMSG #" + self._channel + " :" + message)

	# send /AWAY command to IRC server with optional message (if no message then mark no longer away)
	def setAway(self, message=None):
		if not self._established:
			self._log("can't set IRC away status since connection not established", 1)
			return False

		if message:
			return self._sendMessage("AWAY" + " :" + message)
		else:
			return self._sendMessage("AWAY")
	# send the given line via the socket. don't catch any exceptions.
	def _sendMessageUnsafe(self, message):
		self._log("tx: " + message, 3)
		try:
			self._socket.send(message.encode(self._encoding, errors='ignore') + "\n")
		except Exception as e:
			self._log("failed sending %s: " % (message) + str(e), 1)
			return False
		return True
	
