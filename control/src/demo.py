###############################################################################
#
#   Albow - Demonstration
#
###############################################################################

screen_size = (640, 480)
flags = 0
frame_time = 50 # ms
incr_time = 25 # ms

import os, sys
from os.path import dirname as d
sys.path.insert(1, d(d(os.path.abspath(sys.argv[0]))))

import pygame
pygame.init()
from pygame.color import Color
from pygame.locals import *
from pygame.event import *
from pygame.key import *

from math import pi
from albow.widget import Widget
from albow.controls import Label, Button, Image, AttrRef, \
	RadioButton, ValueDisplay, ProgressBar
from albow.layout import Row, Column, Grid
from albow.fields import TextField, FloatField
from albow.shell import Shell
from albow.screen import Screen
from albow.text_screen import TextScreen
from albow.resource import get_font, get_image
from albow.grid_view import GridView
from albow.palette_view import PaletteView
from albow.image_array import get_image_array
from albow.dialogs import alert, ask
from albow.file_dialogs import \
	request_old_filename, request_new_filename, look_for_file_or_directory
from albow.tab_panel import TabPanel
from albow.table_view import TableView, TableColumn

#--------------------------------------------------------------------------------
#
#    Buttons
#
#--------------------------------------------------------------------------------

class MenuScreen(Screen):

	def __init__(self, shell):
		Screen.__init__(self, shell)
		self.shell = shell
		f1 = get_font(24, "VeraBd.ttf")
		title = Label("Rdrive", font = f1)
		def screen_button(text, screen):
			return Button(text, action = lambda: shell.show_screen(screen))
		menu = Column([
			screen_button("Controls", shell.controls_screen),
			Button("Quit", shell.quit),
		], align = 'l')
		contents = Column([
			title,
			menu,
		], align = 'l', spacing = 20)
		self.add_centered(contents)
	
	def quit(self):
		sys.exit(0)
		
#--------------------------------------------------------------------------------
#
#   Controls
#
#--------------------------------------------------------------------------------

class DemoControlsScreen(Screen):
	model= None
	dir= 0
	old_dir= 0

	def __init__(self, shell):
		Screen.__init__(self, shell)
		self.model = DemoControlsModel()
		width_field = FloatField(ref = AttrRef(self.model, 'width'))
		height_field = FloatField(ref = AttrRef(self.model, 'height'))
		area_display = ValueDisplay(ref = AttrRef(self.model, 'area'), format = "%.2f")
		shape = AttrRef(self.model, 'shape')
		shape_choices = Row([
			RadioButton(setting = 'rectangle', ref = shape), Label("Rectangle"),
			RadioButton(setting = 'triangle', ref = shape), Label("Triangle"),
			RadioButton(setting = 'ellipse', ref = shape), Label("Ellipse"),
			ProgressBar(100, 50, ref = AttrRef(self.model, 'area')),
		])
		grid = Grid([
			[Label("Width"), width_field],
			[Label("Height"), height_field],
			[Label("Shape"), shape_choices],
			[Label("Area"), area_display],
		])
		back = Button("Menu", action = shell.show_menu)
		contents = Column([grid, back])
		self.add_centered(contents)
		width_field.focus()

	def dispatch_key(self, name, event):
		Screen.dispatch_key(self,name,event)

		self.old_dir= self.dir
		
		if event.type == pygame.KEYDOWN and event.dict['key'] == pygame.K_UP:
			self.dir=1
		if event.type == pygame.KEYDOWN and event.dict['key'] == pygame.K_DOWN:
			self.dir= -1
		if event.type == pygame.KEYUP and event.dict['key'] == pygame.K_UP:
			self.dir= 0
		if event.type == pygame.KEYUP and event.dict['key'] == pygame.K_DOWN:
			self.dir= 0

		grid = Grid([
                [Label("Width")],
                [Label("Height")],
                [Label("Shape")],
                [Label("Area")],
        ])
		contents = Column([grid])
		self.add(contents)



	def begin_frame(self):
		if(self.dir==0 and self.model.width>0):
			self.model.width-=2*(frame_time/incr_time)
		elif(self.dir==0 and self.model.width<0):
			self.model.width+=2*(frame_time/incr_time)
		else:
			self.model.width+=self.dir*(frame_time/incr_time)
	
#--------------------------------------------------------------------------------

class DemoControlsModel(object):

	width = 0.0
	height = 0.0
	shape = 'rectangle'

	def get_area(self):
		a = self.width * self.height
		shape = self.shape
		if shape == 'rectangle':
			return a
		elif shape == 'triangle':
			return 0.5 * a
		elif shape == 'ellipse':
			return 0.25 * pi * a
	
	area = property(get_area)

#--------------------------------------------------------------------------------
#
#    Shell
#
#--------------------------------------------------------------------------------

class RdriveShell(Shell):
	def __init__(self, display):
		Shell.__init__(self, display)
		self.create_screens()
		self.menu_screen = MenuScreen(self) # Do this last
		self.set_timer(frame_time)
		self.show_menu()
	
	def create_screens(self):
		self.controls_screen = DemoControlsScreen(self)
	
	def show_menu(self):
		self.show_screen(self.menu_screen)
	
	def begin_frame(self):
		self.controls_screen.begin_frame()

        def send_key(self, widget, name, event):
		Shell.send_key(self, widget, name, event)

def main():
	display = pygame.display.set_mode(screen_size, flags)
	pygame.display.set_caption("Rdrive")
	shell = RdriveShell(display)
	shell.run()

main()
