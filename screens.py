
from math import sin, cos, pi
import time

import pyglet
from pyglet.gl import *

from state import State
from util import *

tick = 0.0

def genericDraw(al):
        global tick
        tick += 1.0

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, vec(0, 500, 0, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE);
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glViewport(0,0,al.width,al.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera
        camx = cos(tick*0.001) * (48.0 * (sin(tick*0.01)+1.0) + 12.0)
        camy = 32.0
        camz = sin(tick*0.001) * (48.0 * (cos(tick*0.01)+1.0) + 12.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, al.width/float(al.height), 0.1, 20000.0)
        gluLookAt(camx, camy, camz, 0,0,0, 0,1,0)

        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glScalef(10,10,10)
        glRotatef(-tick*0.1, 1,0,0)
        glBindTexture(GL_TEXTURE_2D, al.earthTexture.id)
        al.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(20,5,10)
        glScalef(2.7,2.7,2.7)
        glRotatef(tick, 0,1,1)
        glBindTexture(GL_TEXTURE_2D, al.moonTexture.id)
        al.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Roid
        glLoadIdentity()
        glTranslatef(10,20,10)
        glScalef(2,2,2)
        glRotatef(tick*3, 1,1,1)
        glBindTexture(GL_TEXTURE_2D, al.roidTexture.id)
        al.roidGeometry.draw(GL_TRIANGLES)

        # Draw Space
        glLoadIdentity()
        glTranslatef(camx, camy, camz)
        glScalef(19000,19000,19000)
        glBindTexture(GL_TEXTURE_2D, al.spaceTexture.id)
        glDisable(GL_LIGHTING)
        glCullFace(GL_FRONT)
        al.sphereGeometry.draw(GL_TRIANGLES)
        glCullFace(GL_BACK)
        glEnable(GL_LIGHTING)


class Intro(State):
    def __init__(self, al):
        self.al = al
        text  = "Aegis Luna\n\n"
        text += "An alien race is bent on the destruction of humanity. "
        text += "To accomplish their goals, they are teleporting huge asteroids into Earth's gravitational field "
        text += "to fall upon the planet, rendering it inhospitable. Humanity is surprised and overwhelmed by this "
        text += "tactic, and Earth is doomed. People are attempting to escape in spacecraft, but the planet will be obliterated "
        text += "before all of humanity can hope to escape.\n\n"
        text += "In a desperate attempt to delay the inevitable, antigrav mining rigs on the Moon are retrofitted to accelerate "
        text += "the Moon into the asteroids and destroy them.\n\n"
        text += "You are the pilot.\n\n"
        text += "Here are your instructions:\n\n"
        text += "Use the mouse and WASD to steer, and the spacebar to temporarily boost your speed. "
        text += "Earth's shields will gradually recharge, but if the planet is hit while the shields are too low, "
        text += "or if you ever hit the Earth with the Moon, it's curtains.\n\n"
        text += 'Click to continue, or hit escape to quit.'
        self.label = pyglet.text.Label(text, font_size=14, bold=False, multiline=True, width=self.al.width//3,
                                       x=16, y=self.al.height//2, color=(0, 255, 128, 255),
                                       anchor_x='left', anchor_y='center')        
    def on_draw(self):
        genericDraw(self.al)
        glViewport(0,0,self.al.width,self.al.height)
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


class MoonCollision(State):
    def __init__(self, al):
        self.al = al
    def on_draw(self):
        saved =  int(self.al.game.total_time*100)
        text  = 'You destroyed planet Earth by colliding with it. Great job!\n\n'
        text += 'You staved off enough asteroids to save %d people.\n\n' % saved
        text += 'Click to time travel and try again, or hit Escape to leave this mad, mad universe.'
        self.label = pyglet.text.Label(text, font_size=18, bold=True, multiline=True, width=self.al.width//3,
                                       x=self.al.width//2, y=self.al.height//2, color=(255,128,0,255),
                                       anchor_x='center', anchor_y='center')        
        genericDraw(self.al)
        glViewport(0,0,self.al.width,self.al.height)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.al.width, 0, self.al.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.label.draw()
    def on_mouse_press(self, x, y, button, modifiers):
        self.al.newGame()
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.al.exit()


class Apocalypse(State):
    def __init__(self, al):
        self.al = al
    def on_draw(self):
        saved =  int(self.al.game.total_time*100)
        text  = 'Planet Earth has been destroyed, but you staved off enough asteroids to save %d people.\n\n' % saved
        text += 'Click to time travel and try again, or hit Escape to leave this mad, mad universe.'
        self.label = pyglet.text.Label(text, font_size=18, bold=True, multiline=True, width=self.al.width//3,
                                       x=self.al.width//2, y=self.al.height//2, color=(255,128,0,255),
                                       anchor_x='center', anchor_y='center')        
        genericDraw(self.al)
        glViewport(0,0,self.al.width,self.al.height)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.al.width, 0, self.al.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.label.draw()
    def on_mouse_press(self, x, y, button, modifiers):
        self.al.newGame()
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.al.exit()


