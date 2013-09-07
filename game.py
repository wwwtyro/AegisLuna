
import sys
import random

import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

from state import State
from util import *

class Camera:
    def __init__(self):
        self.yaw = 0.0
        self.pitch = pi/4.0
        self.dist = 32.0


class Planetoid:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius
        self.velocity = numpy.zeros(2)
        self.axis = unit(numpy.random.normal(size=3))
        self.rotation = 0.0


class Game(State):

    def __init__(self, al):
        self.al = al
        self.keys = {}
        self.buttons = {}
        self.particles = []
        self.boost = 1.0
        self.camera = Camera()
        self.earthIntegrity = 100.0
        self.total_time = 0.0
        self.initAssets()
        self.initWorld()

    def initAssets(self):
        self.scoreLabel = pyglet.text.Label('', font_size=18, bold=True, x=4.0, y=self.al.height, 
                                            color=(255,255,255,128), anchor_x='left', anchor_y='top')      
        self.integrityLabel = pyglet.text.Label('', font_size=18, bold=True, x=self.al.width-4.0, y=4.0, 
                                                color=(255,0,0,128), anchor_x='right', anchor_y='bottom')      
        self.boostLabel = pyglet.text.Label('', font_size=18, bold=True, x=4.0, y=4.0, 
                                                color=(0,255,255,128), anchor_x='left', anchor_y='bottom')      


    def initWorld(self):
        self.earth = Planetoid(numpy.array([0.,0.]), 10.0)
        self.moon = Planetoid(numpy.array([20.,0.]), 2.7)
        self.roids = []
        self.addRoid()
        self.addRoid()
        self.addRoid()

    def addRoid(self):
        pos = numpy.random.normal(size=2)
        pos /= numpy.linalg.norm(pos)
        pos *= random.random() * 50 + 100
        radius = random.random() * 1.0 + 1.0
        roid = Planetoid(pos, radius)
        roid.speed = (0.1+random.random()*0.1)
        self.roids.append(roid)
        return roid

    def explode(self, x, y, z, color, count, lifespan=100, velocity=None, spread=0.01):
        p = Particles(count=count, 
                      center=[x,y,z], 
                      color=color, 
                      lifespan=lifespan)
        p.explode(velocity, spread)
        self.particles.append(p)

    def on_draw(self):
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
                  self.moon.position[0], 
                  self.moon.radius * 4.0, 
                  self.moon.position[1], 
                  0.0, 1.0, 0.0)

        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glTranslatef(self.earth.position[0], 0, self.earth.position[1])
        glScalef(self.earth.radius, self.earth.radius, self.earth.radius)
        glRotatef(self.earth.rotation, self.earth.axis[0], self.earth.axis[1], self.earth.axis[2])
        glBindTexture(GL_TEXTURE_2D, self.al.earthTexture.id)
        self.al.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(self.moon.position[0], 0, self.moon.position[1])
        glScalef(self.moon.radius, self.moon.radius, self.moon.radius)
        glRotatef(self.moon.rotation, self.moon.axis[0], self.moon.axis[1], self.moon.axis[2])
        glBindTexture(GL_TEXTURE_2D, self.al.moonTexture.id)
        self.al.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Roids
        for roid in self.roids:
            glLoadIdentity()
            glTranslatef(roid.position[0], 0, roid.position[1])
            glScalef(roid.radius, roid.radius, roid.radius)
            glRotatef(roid.rotation, roid.axis[0], roid.axis[1], roid.axis[2])
            glBindTexture(GL_TEXTURE_2D, self.al.roidTexture.id)
            self.al.roidGeometry.draw(GL_TRIANGLES)

        # Draw Space
        glLoadIdentity()
        glTranslatef(camx, camy, camz)
        glScalef(19000,19000,19000)
        glBindTexture(GL_TEXTURE_2D, self.al.spaceTexture.id)
        glDisable(GL_LIGHTING)
        glCullFace(GL_FRONT)
        self.al.sphereGeometry.draw(GL_TRIANGLES)
        glCullFace(GL_BACK)
        glEnable(GL_LIGHTING)

        # Draw Particles
        glPointSize(4.0)
        glPointParameterf(GL_POINT_SIZE_MIN, 1.0)
        glPointParameterf(GL_POINT_SIZE_MAX, 64.0)
        glEnable(GL_POINT_SPRITE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)                                             
        glLoadIdentity()
        glBindTexture(GL_TEXTURE_2D, self.al.pointTexture.id)
        for particle in self.particles:
            particle.particles.draw(GL_POINTS)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_POINT_SPRITE)
        glDepthMask(GL_TRUE)

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
        self.boostLabel.text = "Boost: %d" % int(self.boost * 100)
        self.boostLabel.draw()
        glEnable(GL_LIGHTING)

    def update(self, dt):
        if key.SPACE in self.keys:
            self.boost -= dt
            self.boost = max(self.boost, 0)
        self.total_time += dt
        numroids = int(self.total_time/10) + 3
        while len(self.roids) < numroids:
            self.addRoid()
        dt = 1.0
        dirForce = self.moon.velocity * -0.1
        forward = -numpy.array([cos(self.camera.yaw), sin(self.camera.yaw)])
        forward /= numpy.linalg.norm(forward)
        right = numpy.array([cos(self.camera.yaw - pi/2), sin(self.camera.yaw - pi/2)])
        right /= numpy.linalg.norm(right)
        speed = 0.1
        if key.SPACE in self.keys and self.boost > 0:
            speed *= 4.0
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
        # Check for earth-moon collision
        if numpy.linalg.norm(self.earth.position - self.moon.position) < self.moon.radius + self.earth.radius:
            self.al.boom()
            self.al.activateMoonCollision()
            return
        # Update Roids
        for roid in self.roids[:]:
            # Update velocity.
            v = roid.speed*unit(self.earth.position - roid.position)
            roid.velocity += (v - roid.velocity) * 0.01
            # Update position.
            roid.position += roid.velocity * dt
            # Check for earth collision
            if numpy.linalg.norm(roid.position - self.earth.position) < roid.radius + self.earth.radius:
                self.roids.remove(roid)
                self.earthIntegrity -= random.random() * roid.radius * 15.0
                self.al.boom()
                if int(self.earthIntegrity) < 1:
                    self.al.activateApocalypse()
                    return
                self.explode(roid.position[0], 0, roid.position[1], [1, 0, 0], 400, 1000, roid.velocity*0.0, 0.025)
                self.explode(roid.position[0], 0, roid.position[1], [1, 1, 0], 400, 1000, roid.velocity*0.0, 0.025)
                self.explode(roid.position[0], 0, roid.position[1], [1, 1, 1], 400, 1000, roid.velocity*0.0, 0.025)
            # Check for moon collision
            if numpy.linalg.norm(roid.position - self.moon.position) < roid.radius + self.moon.radius:
                self.roids.remove(roid)
                self.al.boom()
                self.boost += 0.25
                dr = unit(roid.position - self.moon.position)
                dm = unit(self.moon.velocity)
                v = norm(self.moon.velocity) * dr * numpy.dot(dm, dr)
                self.explode(roid.position[0], 0, roid.position[1], [0.5, 0.25, 0], 200, 500, v, 0.1)
                if roid.radius > 1.5:
                    roid1 = self.addRoid()
                    roid2 = self.addRoid()
                    roid1.radius = random.random() * 0.5 + 0.5
                    roid2.radius = random.random() * 0.5 + 0.5
                    roid1.position = self.moon.position + dr * (0.5 + self.moon.radius + 0.5)
                    roid2.position = self.moon.position + dr * (0.5 + self.moon.radius + 0.5)
                    roid1.velocity = v * 2.0 + numpy.random.normal(scale=0.1, size=2)
                    roid2.velocity = v * 2.0 + numpy.random.normal(scale=0.1, size=2)

        # Update Particles.
        for particle in self.particles[:]:
            particle.update()
            if particle.dead:
                self.particles.remove(particle)
        # Update Planetoid rotations
        self.earth.rotation += 0.1
        self.moon.rotation += 0.2
        for roid in self.roids:
            roid.rotation += 8.0

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.buttons[button] = True

    def on_mouse_release(self, x, y, button, modifiers):
        if button in self.buttons:
            del self.buttons[button]

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.al.activateIntro()
        self.keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        del self.keys[symbol]

    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.yaw += dx * 0.001


