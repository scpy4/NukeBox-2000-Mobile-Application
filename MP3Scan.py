#IMPORT ALL OF THE THINGS!
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
from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.scrollview import ScrollView

from functools import partial
import os
import id3reader


# Music button
class MusicButton(Button):

	# Additonal params - Music file name location
	musicFileName = "myFile.mp3"
	pass

class KivyMP3(GridLayout):

	def MyID3(self, fileLoc):

		# Create a scrollable container
		self.scroll = ScrollView(do_scroll_x=(False))

		# Asign the directory to a variable
		self.musicDirectory = fileLoc
		# Create the main wrapper
		self.musicGrid = BoxLayout(orientation="vertical", size_hint=(1,1))
		# Create a grid background to allign the buttons
		xx = GridLayout(cols=1, size_hint=(1, None))
		# Size fix for grid
		xx.bind(minimum_height=xx.setter('height'), minimum_width=xx.setter('width'))
		# Add the grid widget to the scroller 
		self.scroll.add_widget(xx)
		# Artist label
		self.p = Label()
		# Song label
		self.t = Label()
		# Album label
		self.a = Label()
		# Begin the alternating count to alternate the background images (see bellow)
		self.alternate = 1


		# Process each file in the targeted directory 
		for file in os.listdir(self.musicDirectory):

			# Check if the file is an MP3
			if file.endswith(".mp3"):

				# Run ID3 Reader to gather the ID3 data
				id3r = id3reader.Reader(self.musicDirectory + file)

				# Try to gather the artist ID3 data
				try:
					self.p.text = self.stripSquare(id3r.getValue('performer'))
				except:
					self.p.text = "Not Found"

				# Try to gather the song title ID3 data
				try:
					self.t.text = self.stripSquare(id3r.getValue('title'))

				except:
					self.t.text = "Not Found"

				# Try to gather the album ID3 data
				try:
					self.a.text = self.stripSquare(id3r.getValue('album'))
				except:
					self.a.text = "Not Found"

				
				# Create a spawn of the music button class
				self.temp = MusicButton(text="testing", halign="center",
										 size_hint=(1,None), height=("80dp"), 
										 background_normal='images/listone.png',
										 background_down='images/bk.png',
										 markup=True)

				# Set the music buttons filename attribute
				self.temp.musicFileName = file

				# Alternate the background colours
				if self.alternate % 2 == 0:
					self.temp.background_normal='images/listtwo.png'		 
				self.alternate += 1

				# Shorten the Ssong title to prevent overflow.
				self.t.text = self.t.text[:30] + (self.t.text[30:] and '..')

				# Format the music button text
				self.temp.text = "[anchor=title1][size=18sp][color=#4D5158]" + self.t.text + "[/color][/size]\n[color=#AAAAAA]" + self.p.text + "[/color]"
				xx.add_widget(self.temp)

				print "TEST: " + self.temp.text

				# Link the button press and release to events
				self.temp.bind(on_press=self.songSelect, on_release=self.songRelease)


		# Return the newly created window
		return self.scroll

	# Button press action
	def songSelect(self,instance):
		'''
		Button - On Press display a change to acknowledge a registered PRESS
		-	The button is also disabled at this stage to prevent spamming
			the NukeBox 2000 server
		'''
		# Set the background colour on press
		instance.background_color=(1,1,1,.9)
		# Disable the button on press - (Prevent spamming the server)
		instance.disabled = True
	
	# Button release event	
	def songRelease(self,instance):
		'''
		This simple chnages the background color of the button to acknowledge
		a registered RELEASE.
		'''
		# Set the background colour on release
		instance.background_color=(.9,.8,1,.8)

	# Strip square brackets
	def stripSquare(self,item):
		'''
		Remove square brackets from file names.
		This prevents them breaking the format sequence.
		(The strip option didn't work here for some reason, tried multiple combinations of 
		    /[ /] [/]] etc.)
		'''
		# Remove left square bracket
		item = item.replace('[',"")
		# Remove right square bracket
		item = item.replace(']',"")
		# Return the text
		return item

# Application is run as main window
if __name__ == '__main__':

	# Build a Kivy application
    class MyDemo(App):
    	# Define the main nwidget for the Kivy window
        def build(self):

            MyMain = KivyMP3().MyID3("sdcard/Download/")
            Window.size =(300,250)

            # Return the contents to the window
            return MyMain

    # Run the application
    MyDemo().run()