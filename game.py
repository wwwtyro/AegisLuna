
import sys
import random

import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

from util import *

class Planetoid:
    def __init__(self, geometry):
        self.geometry = geometry
        self.radius = 1.0
        self.velocity = numpy.zeros(3)
        self.position = numpy.zeros(3)
        self.rotation = 0.0

class Camera:
    def __init__(self):
        self.up = numpy.array([0, 1, 0])
        self.right = numpy.array([1, 0, 0])
        self.forward = numpy.array([0, 0, 1])
        self.dist = 150.0

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):

        super(Window, self).__init__(*args, **kwargs)
        self.set_exclusive_mouse(True)
        self.set_location(self.screen.width/2 - self.width/2, self.screen.height/2 - self.height/2)
        self.keys = {}
        self.accelerate = False
        self.decelerate = False
        print "building sphere geometry..."
        self.sphereGeometry = buildSphere(32)
        self.earth = Planetoid(self.sphereGeometry)
        self.earth.radius = 100.0
        self.moon = Planetoid(self.sphereGeometry)
        self.moon.radius = 27.0
        self.moon.position[0] = 640.0
        self.roids = []
        roidGeometry = buildAsteroid(32)
        for i in range(10):
            roid = Planetoid(roidGeometry)
            roid.radius = random.random() * 10 + 15
            roid.position = numpy.random.normal(size=3)
            roid.position /= numpy.linalg.norm(roid.position)
            roid.position *= random.random() * 1000 + 150
            self.roids.append(roid)
        self.earthTexture = pyglet.image.load("earth.png").get_mipmapped_texture()
        self.moonTexture = pyglet.image.load("moon.png").get_mipmapped_texture()
        self.spaceTexture = pyglet.image.load("space.png").get_mipmapped_texture()
        self.roidTexture = pyglet.image.load("rock.png").get_mipmapped_texture()
        self.camera = Camera()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        glBindTexture(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, vec(1000, 0, 0, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vec(1, 1, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE);
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glViewport(0,0,self.width,self.height)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera
        campos = self.camera.forward*self.camera.dist + self.moon.position
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width/float(self.height), 0.1, 20000.0)
        gluLookAt(campos[0], campos[1], campos[2], 
                  self.moon.position[0], self.moon.position[1], self.moon.position[2], 
                  self.camera.up[0], self.camera.up[1], self.camera.up[2])
        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glTranslatef(self.earth.position[0], self.earth.position[1], self.earth.position[2])
        glScalef(self.earth.radius, self.earth.radius, self.earth.radius)
        glRotatef(self.earth.rotation, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, self.earthTexture.id)
        self.earth.geometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(self.moon.position[0], self.moon.position[1], self.moon.position[2])
        glScalef(self.moon.radius, self.moon.radius, self.moon.radius)
        glRotatef(self.moon.rotation, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, self.moonTexture.id)
        self.moon.geometry.draw(GL_TRIANGLES)

        # Draw Roids
        for roid in self.roids:
            glLoadIdentity()
            glTranslatef(roid.position[0], roid.position[1], roid.position[2])
            glScalef(roid.radius, roid.radius, roid.radius)
            glRotatef(roid.rotation, 0, 1, 0)
            glBindTexture(GL_TEXTURE_2D, self.roidTexture.id)
            roid.geometry.draw(GL_TRIANGLES)

        # Draw Space
        glLoadIdentity()
        glTranslatef(campos[0], campos[1], campos[2])
        glScalef(19000,19000,19000)
        glBindTexture(GL_TEXTURE_2D, self.spaceTexture.id)
        glDisable(GL_LIGHTING)
        glCullFace(GL_FRONT)
        self.sphereGeometry.draw(GL_TRIANGLES)
        glCullFace(GL_BACK)
        glEnable(GL_LIGHTING)
        return pyglet.event.EVENT_HANDLED

    def update(self, dt):
        dt = 1.0
        self.earth.rotation += 0.1 * dt
        self.moon.rotation += 0.1 * dt
        dirForce = 0.0
        if self.accelerate:
            dirForce = 0.1 * -self.camera.forward
        gforce = self.earth.position - self.moon.position
        gforce = 0.025 * gforce/numpy.linalg.norm(gforce)
        if self.decelerate:
            self.moon.velocity *= 0.9
            gforce = 0.0
            dirForce = 0.0
        self.moon.velocity += (gforce + dirForce) * dt
        self.moon.position += self.moon.velocity * dt
        for roid in self.roids:
            gforce = self.earth.position - roid.position
            gforce = 0.025 * gforce/numpy.linalg.norm(gforce)
            roid.velocity += gforce * dt
            roid.position += roid.velocity * dt
            roid.rotation += 1.0 * dt
        return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.accelerate = True
        if button == 4:
            self.decelerate = True
        return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            self.accelerate = False
        if button == 4:
            self.decelerate = False
        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys.exit()
        return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        return pyglet.event.EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        rotx = RotMatArbAxis(dy * 0.001, self.camera.right)
        self.camera.up = numpy.dot(rotx, self.camera.up)
        self.camera.forward = numpy.dot(rotx, self.camera.forward)
        rotup = RotMatArbAxis(-dx * 0.001, self.camera.up)
        self.camera.right = numpy.dot(rotup, self.camera.right)
        self.camera.forward = numpy.dot(rotup, self.camera.forward)
        self.camera.up /= numpy.linalg.norm(self.camera.up)
        self.camera.right /= numpy.linalg.norm(self.camera.right)
        self.camera.forward /= numpy.linalg.norm(self.camera.forward)
        return pyglet.event.EVENT_HANDLED



# window = Window(fullscreen=True)
window = Window(fullscreen=False, width=1280, height=800)
pyglet.app.run()

