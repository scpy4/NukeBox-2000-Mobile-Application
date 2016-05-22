# A00202022 

# This file was not developed by myself, I believe the original 
# structure is from a Kivy demo (echo) file which was modified to suit
# the NukeBox 2000 application by Darren and I.

# Import Dependencies 
import os.path
import getpass
import pickle

#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor, protocol
from socket import SOL_SOCKET, SO_BROADCAST
from twisted.protocols.basic import LineReceiver
from uuid import getnode as get_mac

class NukeBoxClientProtocol(LineReceiver):

	'''
	NukeBox 2000 Client Protocol Class
	'''

	def __init__(self, factory, fname):

		'''
		Client Protocol constructor method
		'''

		# Create a Reference to the Parent Factory Class
		self.factory = factory

		# Create the Reference to the File
		self.fname = fname

		# Get the Users Name & Mac ID
		self.name = getpass.getuser()
		self.mac = hex(get_mac())

	def connectionMade(self):

		'''
		Called when a connection is made
		'''

		# Get the Size of the File
		filesize = os.path.getsize(self.fname)

		# Serialize the Gathered Data & Send it to the Server
		self.sendLine(pickle.dumps({"size": filesize,
									"filename": self.fname,
									"name": self.name,
									'mac_id': self.mac}
								   ))

	def lineReceived(self, data):

		'''
		Called when a piece of data is received
		'''

		# If the Server Responds with a Request for Transfer, oblige
		if data == 'tx':

			# Open the File
			f = open(self.fname, "rb")

			# Read the File Contents and Send them to the Server
			contents = f.read()
			self.sendLine(contents)

			# Close the File
			f.close()

		# Drop the Connection to the Server
		else:
			self.transport.loseConnection()

	def connectionLost(self, reason):

		'''
		Called when the connection is lost
		'''

		print('Connection Lost')



class NukeBoxClientBroadcastProtocol(protocol.DatagramProtocol):

	'''
	Implements a UDP Broadcaster to locate the NukeBox 2000 Server
	'''

	def __init__(self, factory):

		'''
		Client UDP Protocol constructor method
		'''
		# Create a reference to the Parent Factory
		self.factory = factory

	def startProtocol(self):

		'''
		Set the Socket for UDP Broadcast Packets
		'''

		# Set the Underlying Socket to UDP
		self.transport.socket.setsockopt(SOL_SOCKET,
										 SO_BROADCAST,
										 True)

		# Push out the UDP Packet
		self.sendDatagram()

	def sendDatagram(self):

		'''
		Transmit the UDP Discover Packet
		'''

		# Write the UDP Packet to the Transport
		self.transport.write('Hello Jukebox',
							 ('255.255.255.255', 19009)
							 )

	def datagramReceived(self, data, (ip, port)):

		'''
		Called when a UDP Response is received
		- Uses the Responders address to make TCP Connection
		'''

		# Pull the Server IP Address from the Response & Make the Connection
		self.factory.host = ip
		self.factory.port = port
		reactor.connectTCP(ip, 18008, self.factory)


class NukeBoxClientFactory(protocol.ClientFactory):

	def __init__(self, fname):

		'''
		NukeBoxClient Factory constructor method
		'''

		# Create the Factory Instance Variables
		# self.logger = log
		self.fname = fname
		self.host = ''

	def buildProtocol(self, addr):

		'''
		Responsible for building Client Protocol Instances
		One for each new client
		'''

		# Build an Instance of the Client Protocol
		return NukeBoxClientProtocol(self, self.fname)

	def clientConnectionFailed(self, connector, reason):

		'''
		Attempt to Reconnect when Connections Fail
		'''

		# Call the Connect Method on the Transport obj
		connector.connect()

	def clientConnectionLost(self, connector, reason):

		'''
		Lost Connections are Discarded
		- Stops the Reactor Loop
		'''

		# Call Disconnect method on the Transport obj & Stop the reactor
		connector.disconnect()
		#reactor.stop()

