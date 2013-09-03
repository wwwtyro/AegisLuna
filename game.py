
import sys
import random

import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

from state import State
from util import *


class Planetoid:
    def __init__(self, geometry):
        self.geometry = geometry
        self.radius = 1.0
        self.velocity = numpy.zeros(2)
        self.position = numpy.zeros(2)
        self.rotation = 0.0
        self.rotation_axis = numpy.random.normal(size=3)
        self.rotation_axis /= numpy.linalg.norm(self.rotation_axis)


class Camera:
    def __init__(self):
        self.yaw = 0.0
        self.pitch = pi/4.0
        self.dist = 512.0


class Game(State):

    def __init__(self, al):
        self.al = al
        self.keys = {}
        self.tick = 0.0
        self.sphereGeometry = buildSphere(32)
        self.earth = Planetoid(buildSphere(64))
        self.earth.radius = 300.0
        self.moon = Planetoid(self.sphereGeometry)
        self.moon.radius = 27.0
        self.moon.position[0] = 640.0
        self.roids = []
        self.roidGeometry = buildAsteroid(32)
        self.addAsteroid()        
        self.addAsteroid()        
        self.addAsteroid()        
        self.earthTexture = pyglet.image.load("earth.png").get_mipmapped_texture()
        self.moonTexture = pyglet.image.load("moon.png").get_mipmapped_texture()
        self.spaceTexture = pyglet.image.load("space.png").get_mipmapped_texture()
        self.roidTexture = pyglet.image.load("rock.png").get_mipmapped_texture()
        self.roidCircle = buildCircle([1.0,1.0,0.0,0.5])
        self.camera = Camera()
        self.scoreLabel = pyglet.text.Label('', font_size=18, bold=True, x=4.0, y=self.al.height, 
                                            color=(255,255,255,128), anchor_x='left', anchor_y='top')      
        self.earthIntegrity = 100.0
        self.integrityLabel = pyglet.text.Label('', font_size=18, bold=True, x=self.al.width-4.0, y=4.0, 
                                                color=(255,0,0,128), anchor_x='right', anchor_y='bottom')      
        self.total_time = 0.0

    def addAsteroid(self):
        roid = Planetoid(self.roidGeometry)
        roid.radius = random.random() * 30 + 20
        roid.position = numpy.random.normal(size=2)
        roid.position /= numpy.linalg.norm(roid.position)
        roid.position *= random.random() * 2500 + 2500
        self.roids.append(roid)

    def on_draw(self):
        glBindTexture(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
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
        glViewport(0,0,self.al.width,self.al.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera
        camx = self.moon.position[0] + self.camera.dist * cos(self.camera.yaw) * cos(self.camera.pitch)
        camy = self.camera.dist * sin(self.camera.pitch)
        camz = self.moon.position[1] + self.camera.dist * sin(self.camera.yaw) * cos(self.camera.pitch)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.al.width/float(self.al.height), 0.1, 20000.0)
        gluLookAt(camx, camy, camz, 
                  self.moon.position[0], self.moon.radius * 8.0, self.moon.position[1], 
                  0.0, 1.0, 0.0)
        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glTranslatef(self.earth.position[0], 0, self.earth.position[1])
        glScalef(self.earth.radius, self.earth.radius, self.earth.radius)
        glRotatef(self.earth.rotation, self.earth.rotation_axis[0], 
                  self.earth.rotation_axis[1], self.earth.rotation_axis[2])
        glBindTexture(GL_TEXTURE_2D, self.earthTexture.id)
        self.earth.geometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(self.moon.position[0], 0, self.moon.position[1])
        glScalef(self.moon.radius, self.moon.radius, self.moon.radius)
        glRotatef(self.moon.rotation, self.moon.rotation_axis[0], 
                  self.moon.rotation_axis[1], self.moon.rotation_axis[2])
        glBindTexture(GL_TEXTURE_2D, self.moonTexture.id)
        self.moon.geometry.draw(GL_TRIANGLES)

        # Draw Roids
        for roid in self.roids:
            glLoadIdentity()
            glTranslatef(roid.position[0], 0, roid.position[1])
            glScalef(roid.radius, roid.radius, roid.radius)
            glRotatef(roid.rotation, roid.rotation_axis[0], roid.rotation_axis[1], roid.rotation_axis[2])
            glBindTexture(GL_TEXTURE_2D, self.roidTexture.id)
            roid.geometry.draw(GL_TRIANGLES)

        # Draw Space
        glLoadIdentity()
        glTranslatef(camx, camy, camz)
        glScalef(19000,19000,19000)
        glRotatef(64 + self.tick * 0.005, 0.1, 0.2, 0.3)
        glBindTexture(GL_TEXTURE_2D, self.spaceTexture.id)
        glDisable(GL_LIGHTING)
        glCullFace(GL_FRONT)
        self.sphereGeometry.draw(GL_TRIANGLES)
        glCullFace(GL_BACK)
        glEnable(GL_LIGHTING)

        # Draw GUI
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.al.width, 0, self.al.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.scoreLabel.text = "%d people saved" % int(self.total_time * 100)
        self.scoreLabel.draw()
        self.integrityLabel.color = (int(255*(100-self.earthIntegrity)/100.0), 
                                     int(255*(self.earthIntegrity)/100.0), 0, 128)
        self.integrityLabel.text = "Earth Integrity: %d%%" % int(self.earthIntegrity)
        self.integrityLabel.draw()
        glEnable(GL_LIGHTING)

        return pyglet.event.EVENT_HANDLED

    def update(self, dt):
        self.total_time += dt
        numroids = int(self.total_time/10) + 3
        while len(self.roids) < numroids:
            self.addAsteroid()
        dt = 1.0
        self.tick += dt
        self.earth.rotation += 0.1 * dt
        self.moon.rotation += 0.1 * dt
        dirForce = -self.moon.velocity * 0.05
        forward = -numpy.array([cos(self.camera.yaw), sin(self.camera.yaw)])
        forward /= numpy.linalg.norm(forward)
        right = numpy.array([cos(self.camera.yaw - pi/4), sin(self.camera.yaw - pi/4)])
        right /= numpy.linalg.norm(right)
        speed = 1.0
        if key.W in self.keys:
            dirForce += forward * speed
        if key.S in self.keys:
            dirForce -= forward * speed
        if key.A in self.keys:
            dirForce -= right * speed
        if key.D in self.keys:
            dirForce += right * speed
        self.moon.velocity += dirForce * dt
        self.moon.position += self.moon.velocity * dt
        emag = numpy.linalg.norm(self.earth.position - self.moon.position)
        if emag < self.earth.radius + self.moon.radius:
            self.al.boom()
            self.al.activateMoonCollision()
            return
        for roid in self.roids[:]:
            mvec = roid.position - self.moon.position
            mmag = numpy.linalg.norm(mvec)
            mdir = mvec / mmag
            if mmag*0.9 < self.moon.radius + roid.radius:
                mforce = mdir * numpy.linalg.norm(self.moon.velocity) * 32/roid.radius
                try:
                    self.al.bounce()
                except ALSAException:
                    pass # "File descriptor in bad state" wat
            else:
                mforce = mdir * 0
            emag = numpy.linalg.norm(self.earth.position - roid.position)
            if emag < self.earth.radius + roid.radius:
                self.earthIntegrity -= roid.radius/2.0
                self.al.boom()
                if int(self.earthIntegrity) < 1:
                    self.al.activateApocalypse()
                    return
                self.roids.remove(roid)
                continue
            gforce = self.earth.position - roid.position
            gforce = 0.025 * gforce/numpy.linalg.norm(gforce)
            dforce = roid.velocity * -0.01
            roid.velocity += (mforce + dforce + gforce) * dt
            roid.position += roid.velocity * dt
            roid.rotation += 4.0 * dt
        return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.al.activateIntro()
        self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        del self.keys[symbol]

    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.yaw += dx * 0.001


