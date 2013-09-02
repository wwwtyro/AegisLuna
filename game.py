
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

class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):

        super(Window, self).__init__(*args, **kwargs)
        self.set_exclusive_mouse(True)
        self.set_location(self.screen.width/2 - self.width/2, self.screen.height/2 - self.height/2)
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
        self.roidLabel = pyglet.text.Label('0 roids',
                                            font_size=18, bold=True,
                                            x=self.width - 4.0, y=self.height, color=(255,0,0,255),
                                            anchor_x='right', anchor_y='top')        
        self.scoreLabel = pyglet.text.Label('0 points',
                                            font_size=18, bold=True,
                                            x=4.0, y=self.height, color=(255,255,0,255),
                                            anchor_x='left', anchor_y='top')        
        self.score = 0
        pyglet.clock.schedule_interval(self.update, 1/60.0)
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
        glViewport(0,0,self.width,self.height)

    def addAsteroid(self):
            roid = Planetoid(self.roidGeometry)
            roid.radius = random.random() * 30 + 20
            roid.position = numpy.random.normal(size=2)
            roid.position /= numpy.linalg.norm(roid.position)
            roid.position *= random.random() * 2500 + 2500
            self.roids.append(roid)

    def on_draw(self):
        window.clear()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camera
        camx = self.moon.position[0] + self.camera.dist * cos(self.camera.yaw) * cos(self.camera.pitch)
        camy = self.camera.dist * sin(self.camera.pitch)
        camz = self.moon.position[1] + self.camera.dist * sin(self.camera.yaw) * cos(self.camera.pitch)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.width/float(self.height), 0.1, 20000.0)
        gluLookAt(camx, camy, camz, 
                  self.moon.position[0], self.moon.radius * 8.0, self.moon.position[1], 
                  0.0, 1.0, 0.0)
        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glTranslatef(self.earth.position[0], 0, self.earth.position[1])
        glScalef(self.earth.radius, self.earth.radius, self.earth.radius)
        glRotatef(self.earth.rotation, self.earth.rotation_axis[0], self.earth.rotation_axis[1], self.earth.rotation_axis[2])
        glBindTexture(GL_TEXTURE_2D, self.earthTexture.id)
        self.earth.geometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(self.moon.position[0], 0, self.moon.position[1])
        glScalef(self.moon.radius, self.moon.radius, self.moon.radius)
        glRotatef(self.moon.rotation, self.moon.rotation_axis[0], self.moon.rotation_axis[1], self.moon.rotation_axis[2])
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

        # Indicator lines
        # glLoadIdentity()
        # glDisable(GL_LIGHTING)
        # glDisable(GL_TEXTURE_2D)
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glLineWidth(1.0)
        # for roid in self.roids:
        #     glLoadIdentity()
        #     glTranslatef(roid.position[0], 0, roid.position[1])
        #     glScalef(roid.radius*2, 0, roid.radius*2)
        #     self.roidCircle.draw(GL_LINE_LOOP)
        # glEnable(GL_TEXTURE_2D)
        # glEnable(GL_LIGHTING)

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
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.scoreLabel.text = "%d points" % self.score
        self.scoreLabel.draw()
        self.roidLabel.text = "%d asteroids" % len(self.roids)
        self.roidLabel.draw()
        glEnable(GL_LIGHTING)

        return pyglet.event.EVENT_HANDLED

    def update(self, dt):
        self.score += dt * len(self.roids)
        dt = 1.0
        self.tick += dt
        if int(self.tick) % 1000 == 0:
            self.addAsteroid()
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
        gforce = self.earth.position - self.moon.position
        gforce = 0#0.1 * gforce/numpy.linalg.norm(gforce)
        self.moon.velocity += (gforce + dirForce) * dt
        self.moon.position += self.moon.velocity * dt
        for roid in self.roids:
            mvec = roid.position - self.moon.position
            mmag = numpy.linalg.norm(mvec)
            mdir = mvec / mmag
            if mmag*0.9 < self.moon.radius + roid.radius:
                mforce = mdir * numpy.linalg.norm(self.moon.velocity) * 32/roid.radius
            else:
                mforce = mdir * 0
            gforce = self.earth.position - roid.position
            gforce = 0.025 * gforce/numpy.linalg.norm(gforce)
            dforce = roid.velocity * -0.01
            roid.velocity += (mforce + dforce + gforce) * dt
            roid.position += roid.velocity * dt
            roid.rotation += 4.0 * dt
        return pyglet.event.EVENT_HANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        return pyglet.event.EVENT_HANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            sys.exit()
        self.keys[symbol] = True
        return pyglet.event.EVENT_HANDLED

    def on_key_release(self, symbol, modifiers):
        del self.keys[symbol]
        return pyglet.event.EVENT_HANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        self.camera.yaw += dx * 0.001
        return pyglet.event.EVENT_HANDLED



# window = Window(fullscreen=True)
window = Window(fullscreen=False, width=1280, height=800)
pyglet.app.run()

