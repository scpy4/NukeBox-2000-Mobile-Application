
import os.path
import getpass
import pickle

#install_twisted_rector must be called before importing the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


#A simple Client that send messages to the echo server
from twisted.internet import reactor, protocol
from socket import SOL_SOCKET, SO_BROADCAST
from twisted.protocols.basic import LineReceiver

#class EchoClient(protocol.Protocol):
class NukeBoxClientProtocol(LineReceiver):

	'''
	NukeBox 2000 Client Protocol Class
	'''

	def __init__(self, factory, fname):

		'''
		Client Protocol constructor method
		'''

		# Create the Instance Variables

		# Create a Reference to the Parent Factory Class
		self.factory = factory

		# Create the Reference to the File
		self.fname = fname
		#self.fname = "//sdcard/Download/Mike.mp3"

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



# Class to send a broadcast message and return the server 


#class ClientBroadcastProtocol(protocol.DatagramProtocol):

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

#class EchoFactory(protocol.Factory):
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


# Import Kivy Dependencies
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout #NB
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.loader import Loader
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform

from MP3Scan import KivyMP3
from functools import partial

from kivy.uix.filechooser import FileChooserIconView, FileChooserListView


from uuid import getnode as get_mac

# Main application class
class NukeBoxApp(App, KivyMP3):

	'''
	This is the main application class for the NukeBox 2000 mobile application.
	-	This inherits the Kivys main app class and a custom KivyMP3 class which
		provides a simpler way to view and interact with MP3's on a device.
	'''
	connection = None

	# Built in Kivy Method
	def build(self):

		# Assign the setup method
		root = self.setup_gui()

		#Return the Window built inside setup_gui
		return root	

	# Define the setup method.
	def setup_gui(self):
		'''
		The setup method is used to essentially build the applications.
		-	Widgets are created and assigned to containers.
		-	Layering of containers provides additional functionality such as the
			spring feature when dragging down on the file browser
		'''

		# Check the operating system and set the file directory prefix.
		
		# System is Linux
		if platform == "linux":
			self.prefix = "sdcard/"
			# set the window size to a mobile ratio
			Window.size =(432,768)

		# System is Android
		else:
			self.prefix = "/sdcard/"

		# Get the MAC Address in hex format.
		self.mac = hex(get_mac())

		# Create the main wrapper
		self.wrap = GridLayout(cols=1, rows=4)

		# Create the Carosel
		self.carousel = Carousel(direction='right',size_hint=(1,.7), loop="True",
								anim_move_duration=(.1), anim_cancel_duration=(.1),min_move=(.1),scroll_distance=("20dp"),scroll_timeout=(100))

		# Carosel One - Downloads Folder
		self.slideOne = BoxLayout(orientation="vertical", size_hint=(1,1))
		self.scro = KivyMP3.MyID3(self,str(self.prefix)+"Download/")
		self.slideOne.add_widget(self.scro)
		self.carousel.add_widget(self.slideOne)

		# Carosel Two - Music Folder
		self.scro2 = KivyMP3.MyID3(self,str(self.prefix)+"Music/")
		self.slideTwo = BoxLayout(orientation="vertical")
		self.carousel.add_widget(self.slideTwo)
		self.slideTwo.add_widget(self.scro2)

		# Create Header Image
		header = BoxLayout(orientation="vertical",size_hint=(1,.1))
		headerImage = Button(background_normal="./images/header.png", background_down="./images/header.png",
								size_hint=(1,1))
		header.add_widget(headerImage)

		# Create Header Buttons - (These Emlulate Tab Buttons)
		headerBtns = BoxLayout (orientation="horizontal",size_hint=(1,.1))
		headerBtnOne = Button(text="Downloads", size_hint=(.5,1),background_normal='images/tabone.png',background_down='images/tabtwo.png')
		headerBtnTwo = Button(text="Music", size_hint=(.5,1),background_normal='images/tabone.png',background_down='images/tabtwo.png')
		headerBtns.add_widget(headerBtnOne)
		headerBtns.add_widget(headerBtnTwo)

		#self.layout = BoxLayout(orientation='vertical',size_hint=(1,.5))
		#self.layout2 = BoxLayout(orientation='vertical',size_hint=(1,.5),padding=20)

		# Button Box
		self.ButtonAnchorLayout = AnchorLayout(anchor_x='center', anchor_y='bottom',size_hint=(1,.1))
		self.ButtonLayout = BoxLayout(orientation="horizontal",size_hint=(1,1))
		self.btn = Button(background_normal="./images/footer.png", background_down="./images/footer.png",
			size_hint=(1,1))

		self.ButtonLayout.add_widget(self.btn)

		self.ButtonAnchorLayout.add_widget(self.ButtonLayout)


		# File Browser / Selection 

		# While the KivyMP3 file overwrites this functionality I decided to
		# 	leave it within the file as a third slide to provde access to
		# 	non-traditional folders.

		self.sel = FileChooserListView(rootpath=str(self.prefix)+"Download/",filters=["*.mp3"])
		self.carousel.add_widget(self.sel)
		self.sel.bind(on_submit=self.fileSelect)

		# Add Items to main
		self.wrap.add_widget(header)
		self.wrap.add_widget(headerBtns)
		# Add Carosel to Grid Layout
		self.wrap.add_widget(self.carousel)
		self.wrap.add_widget(self.ButtonAnchorLayout)

		# Assign events to methods
		headerBtnOne.bind(on_press = partial(self.swTab,0))
		headerBtnTwo.bind(on_press = partial(self.swTab,1))

		# Return the newly created window
		return self.wrap

	#=======================#
	#		Events			#
	#=======================#

	def songSelect(self,instance):
		'''
		This builds upon the KivyMP3 method, introducing some custom
		specifically for this application. 
		'''

		if self.carousel.index == 0:
			fileDir = str(self.prefix)+"Download/" + str(instance.musicFileName)
		elif self.carousel.index == 1:
			fileDir = str(self.prefix)+"Music/" + str(instance.musicFileName)

		# Call the Twisted network transfer method
		self.twistIt(fileDir)


	# Switch tabs
	def swTab(self,slideValue,instance):
		'''
		Switch file viewer depending if not on current
		'''

		if self.carousel.index != slideValue:
			self.carousel.load_slide(self.carousel.slides[slideValue])


	# Allow application pause/minimise on Android systems
	def on_pause(self):
		'''
		This is required to keep the application in an "Alive state" while 
		minimized on Android systmes.
		'''
		return True

	#File Selected - Gather the path
	def fileSelect(self,kivyObject,selectedDir,position):

		'''
		The object of this method is to gather the file information, once this has been established
		the file is transfered over the network using twisted.
		'''

		# Process the directory
		self.direct = selectedDir[0]
		x = self.direct
		x = self.direct.split("/")

		# Print the file name 
		print x[-1]

		# Print the directory in full
		self.direct = str(x[-1])
		print ("File Directory: " + selectedDir[0])

		self.twistIt(selectedDir[0])

	# Call twisted functionality
	def twistIt(self,fileValue):
		# Define the factory
		self.factory = NukeBoxClientFactory(fileValue)
		# Set up protocol
		self.udp_protocol = NukeBoxClientBroadcastProtocol(self.factory)
		# Listen for the server
		reactor.listenUDP(0, self.udp_protocol)

	# Display message on connectself.stripSquare
	def connect_to_server(self, ip):
				
		print 'Connect To Server Function ' + str(ip)

	def on_connection(self, connection):
		self.print_message("connected succesfully!")
		self.connection = connection

# Application is run as main window
if __name__ == '__main__':
	NukeBoxApp().run()
