# A00202022

# Import Dependencies
from kivyTwisted import *
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
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from MP3Scan import KivyMP3
from functools import partial
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
		'''
		Build method is required by Kivy, it returns the main widget to the window.
		'''

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
		self.browserOne = KivyMP3.MyID3(self,str(self.prefix)+"Download/")
		self.slideOne.add_widget(self.browserOne)
		self.carousel.add_widget(self.slideOne)

		# Carosel Two - Music Folder
		self.browserTwo = KivyMP3.MyID3(self,str(self.prefix)+"Music/")
		self.slideTwo = BoxLayout(orientation="vertical")
		self.carousel.add_widget(self.slideTwo)
		self.slideTwo.add_widget(self.browserTwo)

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

		# Button Box
		
		# Anchor to bottom of screen
		self.ButtonAnchorLayout = AnchorLayout(anchor_x='center', anchor_y='bottom',size_hint=(1,.1))
		
		# Footer
		self.ButtonLayout = BoxLayout(orientation="horizontal",size_hint=(1,1))
		self.btn = Button(background_normal="./images/footer.png", background_down="./images/footer.png",
			size_hint=(1,1))
		# Footer layout
		self.ButtonLayout.add_widget(self.btn)
		self.ButtonAnchorLayout.add_widget(self.ButtonLayout)


		# File Browser / Selection 

		# While the KivyMP3 file overwrites this functionality I decided to
		# 	leave it within the file as a third slide to provde access to
		# 	non-traditional folders.

		# Call the file browser - set the default path to the root and only view MP3s
		self.fileBrowse = FileChooserListView(rootpath="/", filters=["*.mp3"])
		self.carousel.add_widget(self.fileBrowse)
		self.fileBrowse.bind(on_submit=self.fileSelect)

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
	#		Methods			#
	#=======================#
	
	# Song selection method
	def songSelect(self,instance):
		'''
		This builds upon the KivyMP3 method, introducing some custom
		specifically for this application. The method takes the instance
		value by default:
		-	Instance value of the button being pressed.
		'''

		if self.carousel.index == 0:
			fileDir = str(self.prefix)+"Download/" + str(instance.musicFileName)
		elif self.carousel.index == 1:
			fileDir = str(self.prefix)+"Music/" + str(instance.musicFileName)

		# Call the Twisted network transfer method
		self.twistIt(fileDir)


	# Switch tabs
	def swTab(self, slideValue, instance):
		'''
		Switches the carousel depending on which slide is n view.
		The method takes two additional attributes:
		-	The target slide for the button press.
		-	The instance of the item (Kivy)
		'''
		
		try:
			if self.carousel.index != slideValue:
				self.carousel.load_slide(self.carousel.slides[slideValue])
		except:
			pass


	# Allow application pause/minimise on Android systems
	def on_pause(self):
		
		'''
		This is required to keep the application in an "Alive state" while 
		minimized on Android systmes.
		'''
		
		return True

	#File Selected - Gather the path
	def fileSelect(self, kivyObject, selectedDir, position):

		'''
		The object of this method is to gather the file information, 
		once this has been established the file is transfered over the 
		network using twisted. 
		
		The method takes 3 variables by default(Kivy):
		-	The instance information.
		-	The selected directory location.		
		-	The positional informaiton
		'''

		# Process the directory information
		self.direct = selectedDir[0]
		x = self.direct
		x = self.direct.split("/")
		self.direct = str(x[-1])
		
		# Call Twisted
		self.twistIt(selectedDir[0])

	# Call twisted functionality
	def twistIt(self,fileValue):
		
		'''
		This method calls the Twisted functionality of the program.
		-	The method takes onf additional value representing the files locaiton.
		'''
		
		# Define the factory
		self.factory = NukeBoxClientFactory(fileValue)
		# Set up protocol
		self.udp_protocol = NukeBoxClientBroadcastProtocol(self.factory)
		# Listen for the server
		reactor.listenUDP(0, self.udp_protocol)


# Application is run as main window
if __name__ == '__main__':
	
	NukeBoxApp().run()
