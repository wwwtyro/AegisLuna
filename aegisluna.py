#!/usr/bin/env python

import sys
import glob

try:
    import numpy
except:
    print "Aegis Luna cannot run, because it looks like numpy is not installed."
    sys.exit()

import pyglet
from pyglet.gl import *
from pyglet.window import key


from screens import *
from util import *
from game import Game

class AegisLuna(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(AegisLuna, self).__init__(*args, **kwargs)
        self.prepareAssets()
        self.set_exclusive_mouse(True)
        self.set_location(self.screen.width/2 - self.width/2, self.screen.height/2 - self.height/2)
        self.intro = Intro(self)
        self.moonCollision = MoonCollision(self)
        self.apocalypse = Apocalypse(self)
        self.game = Game(self)
        self.currentState = None
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        self.activateIntro()

    def prepareAssets(self):
        self.earthTexture = pyglet.image.load("assets/earth.png").get_mipmapped_texture()
        self.moonTexture = pyglet.image.load("assets/moon.png").get_mipmapped_texture()
        self.spaceTexture = pyglet.image.load("assets/space.png").get_mipmapped_texture()
        self.roidTexture = pyglet.image.load("assets/rock.png").get_mipmapped_texture()
        self.pointTexture = pyglet.image.load("assets/point.png").get_mipmapped_texture()
        self.sphereGeometry = buildSphere(32)
        self.roidGeometry = buildAsteroid(32)
        self.spaceSound = pyglet.resource.media('assets/space.wav', streaming=False)
        self.spacePlayer = pyglet.media.Player()
        self.spacePlayer.queue(self.spaceSound)
        self.spacePlayer.eos_action = self.spacePlayer.EOS_LOOP
        self.spacePlayer.play()

    def boom(self):
        pyglet.resource.media('assets/boom.wav', streaming=False).play()

    def activateIntro(self):
        self.currentState = self.intro

    def activateGame(self):
        self.currentState = self.game

    def activateMoonCollision(self):
        self.currentState = self.moonCollision

    def activateApocalypse(self):
        self.currentState = self.apocalypse

    def newGame(self):
        self.game = Game(self)
        self.currentState = self.game

    def exit(self):
        sys.exit()

    def update(self, dt):
        if self.currentState:
            self.currentState.update(dt)

    def on_draw(self):
        if self.currentState:
            self.currentState.on_draw()
            return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if self.currentState:
            self.currentState.on_mouse_press(x, y, button, modifiers)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.currentState:
            self.currentState.on_mouse_drag(x, y, dx, dy, button, modifiers)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if self.currentState:
            self.currentState.on_mouse_release(x, y, button, modifiers)
            return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.X:
            c = len(glob.glob('screenshot*.png'))
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot%s.png' % c)            
        if self.currentState:
            self.currentState.on_key_press(symbol, modifiers)
            return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        if self.currentState:
            self.currentState.on_key_release(symbol, modifiers)
            return pyglet.event.EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        if self.currentState:
            self.currentState.on_mouse_motion(x, y, dx, dy)
            return pyglet.event.EVENT_HANDLED

    def on_resize(self, width, height):
        if self.currentState:
            self.currentState.on_resize(width, height)
            return pyglet.event.EVENT_HANDLED

def main():
    al = AegisLuna(fullscreen=True)
    pyglet.app.run()


if __name__ == "__main__":
    main()