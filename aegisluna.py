
import sys

import pyglet

from screens import *
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
        self.spaceSound = pyglet.resource.media('space.wav', streaming=False)
        self.spacePlayer = None

    def boom(self):
        pyglet.resource.media('boom.wav', streaming=False).play()

    def bounce(self):
        pyglet.resource.media('bounce.wav', streaming=False).play()

    def spaceOn(self):
        if self.spacePlayer is None:
            self.spacePlayer = pyglet.media.Player()
            self.spacePlayer.queue(self.spaceSound)
            self.spacePlayer.eos_action = self.spacePlayer.EOS_LOOP
        if not self.spacePlayer.playing:
            self.spacePlayer.play()
    def spaceOff(self):
        if self.spacePlayer is None:
            return
        if self.spacePlayer.playing:
            self.spacePlayer.pause()

    def activateIntro(self):
        self.spaceOff()
        self.currentState = self.intro

    def activateGame(self):
        self.spaceOn()
        self.currentState = self.game

    def activateMoonCollision(self):
        self.spaceOff()
        self.currentState = self.moonCollision

    def activateApocalypse(self):
        self.spaceOff()
        self.currentState = self.apocalypse

    def newGame(self):
        self.spaceOn()
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
        

def main():
    # al = AegisLuna(fullscreen=True)
    al = AegisLuna(fullscreen=False, width=1280, height=800)
    pyglet.app.run()


if __name__ == "__main__":
    main()