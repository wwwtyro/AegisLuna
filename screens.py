
import pyglet
from pyglet.gl import *

from state import State

class Intro(State):

    def __init__(self, al):
        self.al = al
        text  = 'Aegis Luna\n\n'
        text += 'Instructions: use the mouse and WASD to steer. Protect Earth from incoming '
        text += 'asteroids by colliding the moon with them!\n\n'
        text += 'Click to continue, or hit escape to quit.'
        self.label = pyglet.text.Label(text, font_size=18, bold=False, multiline=True, width=self.al.width//3,
                                       x=self.al.width//2, y=self.al.height//2, color=(0,128,0,255),
                                       anchor_x='center', anchor_y='center')        

    def update(self, dt):
        pass

    def on_draw(self):
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE);
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glViewport(0,0,self.al.width,self.al.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.al.width, 0, self.al.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.al.activateGame()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.al.exit()
