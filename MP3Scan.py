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

		self.scroll = ScrollView(do_scroll_x=(False))
		self.musicDirectory = fileLoc
		# Create the main wrapper
		self.musicGrid = BoxLayout(orientation="vertical", size_hint=(1,1))
		#self.bind(minimum_height=self.musicGrid.setter("height") ,minimum_width=self.musicGrid.setter("width"))
		xx = GridLayout(cols=1, size_hint=(1, None))
		xx.bind(minimum_height=xx.setter('height'), minimum_width=xx.setter('width'))
		self.scroll.add_widget(xx)
		self.p = Label(text="Test")
		self.t = Label()
		self.a = Label()
		self.alternate = 1

		for file in os.listdir(self.musicDirectory):

			#self.temp = Button(text="tetsing",size_hint=(1,.2))

			if file.endswith(".mp3"):
				print(file)

				id3r = id3reader.Reader(self.musicDirectory + file)

				print "Artist: %s" % id3r.getValue('performer')
				print "Album: %s" % id3r.getValue('album')
				print "Track: %s" % id3r.getValue('title')

				try:
					self.p.text = self.stripSquare(id3r.getValue('performer'))
				except:
					self.p.text = "None Found"
				try:
					self.t.text = self.stripSquare(id3r.getValue('title'))

				except:
					self.t.text = "None Found"
				try:
					self.a.text = self.stripSquare(id3r.getValue('album'))
				except:
					self.a.text = "Non Found"

				
				
				self.temp = MusicButton(text="testing", halign="center",
										 size_hint=(1,None), height=("80dp"), 
										 background_normal='images/listone.png',
										 background_down='images/bk.png',
										 markup=True)

				self.temp.musicFileName = file

				if self.alternate % 2 == 0:

					self.temp.background_normal='images/listtwo.png'			 
											 
				self.alternate += 1


				# Shorten the Title
				self.t.text = self.t.text[:30] + (self.t.text[30:] and '..')

				self.temp.text = "[anchor=title1][size=18sp][color=#4D5158]" + self.t.text + "[/color][/size]\n[color=#AAAAAA]" + self.p.text + "[/color]"
				xx.add_widget(self.temp)
				print "TEST: " + self.temp.text
				self.temp.bind(on_press=self.songSelect, on_release=self.songRelease)


		# Return the newly created window
		return self.scroll

	# Actions
	def songSelect(self,instance):

		instance.background_color=(1,1,1,.9)
		print "Clicked"
		print instance.musicFileName
		
	def songRelease(self,instance):
		instance.background_color=(.9,.8,1,.8)


	def stripSquare(self,item):
		'''
		Remove square brackets from file names.
		This prevents them breaking the format sequence.
		(strip didn't work here for some reason, tried multiple combinations of 
		    /[ /] [/]] etc.)
		'''
		item = item.replace('[',"")
		item = item.replace(']',"")
		return item


if __name__ == '__main__':


    class MyDemo(App):

        def build(self):

            MyMain = KivyMP3().MyID3("sdcard/Download/")
            Window.size =(300,250)

            return MyMain

    MyDemo().run()


