#!/usr/bin/env python

"""
a class that renders text as a progress bar. after creating of the
instance of the class by passing the font, message, color, and bgcolor.
you call the "render" method, and pass it a percentage from 0 to 100.

note that the uncompleted section of the text is drawn with the bgcolor,
the rest of the text is done using the given color, and highlights when
finished (progress >= 100)
"""
import os, sys, pygame, pygame.font, pygame.image
from pygame.locals import *

class TextProgress:
    def __init__(self, font, message, color, bgcolor):
        self.font = font
        self.message = message
        self.color = color
        self.bgcolor = bgcolor
        self.offcolor = [c^40 for c in color]
        self.notcolor = [c^0xFF for c in color]
        self.text = font.render(message, 0, (255,0,0), self.notcolor)
        self.text.set_colorkey(1)
        self.outline = self.textHollow(font, message, color)
        self.bar = pygame.Surface(self.text.get_size())
        self.bar.fill(self.offcolor)
        width, height = self.text.get_size()
        stripe = Rect(0, height/2, width, height/4)
        self.bar.fill(color, stripe)
        self.ratio = width / 100.0

    def textHollow(self, font, message, fontcolor):
        base = font.render(message, 0, fontcolor, self.notcolor)
        size = base.get_width() + 2, base.get_height() + 2
        img = pygame.Surface(size, 16)
        img.fill(self.notcolor)
        base.set_colorkey(0)
        img.blit(base, (0, 0))
        img.blit(base, (2, 0))
        img.blit(base, (0, 2))
        img.blit(base, (2, 2))
        base.set_colorkey(0)
        base.set_palette_at(1, self.notcolor)
        img.blit(base, (1, 1))
        img.set_colorkey(self.notcolor)
        return img

    def render(self, percent=50):
        surf = pygame.Surface(self.text.get_size())
        if percent < 100:
            surf.fill(self.bgcolor)
            surf.blit(self.bar, (0,0), (0, 0, percent*self.ratio, 100))
        else:
            surf.fill(self.color)
        surf.blit(self.text, (0,0))
        surf.blit(self.outline, (-1,-1))
        surf.set_colorkey(self.notcolor)
        return surf



entry_info = 'Progress, by Pete Shinners'

#this code will display our work, if the script is run...
if __name__ == '__main__':
    import random
    pygame.init()

    #create our fancy text renderer
    bigfont = pygame.font.Font(None, 60)
    white = 255, 255, 255
    renderer = TextProgress(bigfont, entry_info, white, (40, 40, 40))
    text = renderer.render(0)

    #create a window the correct size
    win = pygame.display.set_mode(text.get_size())
    win.fill((50,100,50), (0, 0, 600, 28))
    win.blit(text, (0, 0))
    pygame.display.flip()

    progress = 1;

    #wait for the finish
    finished = 0
    while not finished:
        pygame.time.delay(40)
        for event in pygame.event.get():
            if event.type is KEYDOWN and event.key == K_s: #save it
                name = os.path.splitext(sys.argv[0])[0] + '.bmp'
                print 'Saving image to:', name
                pygame.image.save(win, name)
            elif event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
                finished = 1
        
        progress = (progress + random.randint(0,3)) % 120
        text = renderer.render(progress)
        win.blit(text, (0, 0))
        pygame.display.flip()
