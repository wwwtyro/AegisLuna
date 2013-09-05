
import sys
import random

import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

from state import State
from util import *

from Box2D import *


class Camera:
    def __init__(self):
        self.yaw = 0.0
        self.pitch = pi/4.0
        self.dist = 20.0


class Planetoid:
    def __init__(self, game, kind, position, radius, density=1.0, friction=0.3, restitution=1.0, damping=0.5):
        self.game = game
        self.kind = kind
        self.world = self.game.world
        self.radius = radius
        bodyDef = b2BodyDef()
        bodyDef.position = b2Vec2(list(position))
        self.body = self.world.CreateBody(bodyDef)
        shapeDef = b2CircleDef()
        shapeDef.radius = radius
        shapeDef.density = density
        shapeDef.friction = friction
        shapeDef.restitution = restitution
        self.shape = self.body.CreateShape(shapeDef)
        self.body.SetMassFromShapes()
        self.body.linearDamping = damping
        self.redraw = False
        self.game.b2Shapes[self.shape] = self
    def destroy(self):
        del self.game.b2Shapes[self.shape]


class ContactListener(b2ContactListener):
    def __init__(self, game): 
        self.game = game
        super(ContactListener, self).__init__() 
    def Add(self, point):
        poid1 = self.game.b2Shapes[point.shape1]
        poid2 = self.game.b2Shapes[point.shape2]
        kinds = [poid1.kind, poid2.kind]
        if 'earth' in kinds and 'moon' in kinds:
            self.game.al.boom()
            self.game.al.activateMoonCollision()
            return
        if 'roid' in kinds and 'moon' in kinds:
            self.game.al.bounce()
            if poid1.kind == 'roid':
                roid = poid1
            else:
                roid = poid2
            self.game.explode(roid.body.position.x, 0, roid.body.position.y, [0.5, 0.25, 0.0], 1000, 100)
        if 'roid' in kinds and 'earth' in kinds:
            if poid1.kind == 'roid':
                roid = poid1
            else:
                roid = poid2
            roid.dead = True
            self.game.earthIntegrity -= random.random() * 30.0
            self.game.al.boom()
            self.game.explode(roid.body.position.x, 0, roid.body.position.y, [1, 0, 0], 3000, 200)
            self.game.explode(roid.body.position.x, 0, roid.body.position.y, [1, 1, 0], 2000, 300)
            self.game.explode(roid.body.position.x, 0, roid.body.position.y, [1, 1, 1], 1000, 400)
            if int(self.game.earthIntegrity) < 1:
                self.game.al.activateApocalypse()

class Game(State):

    def __init__(self, al):
        self.al = al
        self.keys = {}
        self.b2Shapes = {}
        self.particles = []
        self.camera = Camera()
        self.earthIntegrity = 100.0
        self.total_time = 0.0
        self.loadAssets()
        self.buildAssets()
        self.initWorld()

    def loadAssets(self):
        self.earthTexture = pyglet.image.load("earth.png").get_mipmapped_texture()
        self.moonTexture = pyglet.image.load("moon.png").get_mipmapped_texture()
        self.spaceTexture = pyglet.image.load("space.png").get_mipmapped_texture()
        self.roidTexture = pyglet.image.load("rock.png").get_mipmapped_texture()

    def buildAssets(self):
        self.sphereGeometry = buildSphere(32)
        self.roidGeometry = buildAsteroid(32)
        self.scoreLabel = pyglet.text.Label('', font_size=18, bold=True, x=4.0, y=self.al.height, 
                                            color=(255,255,255,128), anchor_x='left', anchor_y='top')      
        self.integrityLabel = pyglet.text.Label('', font_size=18, bold=True, x=self.al.width-4.0, y=4.0, 
                                                color=(255,0,0,128), anchor_x='right', anchor_y='bottom')      

    def initWorld(self):
        b2_velocityThreshold = 0.00001
        worldAABB = b2AABB()
        worldAABB.lowerBound = (-10000, -10000)
        worldAABB.upperBound = (10000, 10000)
        self.world = b2World(worldAABB, b2Vec2(0.0, 0.0), False)
        self.cl = ContactListener(self)
        self.world.SetContactListener(self.cl)
        self.b2Earth = Planetoid(self, 'earth', [0.0,0.0], 10.0, density=0.0)
        self.b2Moon = Planetoid(self, 'moon', [20.0,0.0], 1.0, density=1.0, restitution=1.0, damping=0.05)
        self.b2Roids = []
        self.addRoid()
        self.addRoid()
        self.addRoid()

    def addRoid(self):
        pos = numpy.random.normal(size=2)
        pos /= numpy.linalg.norm(pos)
        pos *= random.random() * 50 + 100
        radius = random.random() * 0.5 + 0.5
        roid = Planetoid(self, 'roid', pos, radius, density=1.0, restitution=1.0, damping = 0.01)
        roid.dead = False
        self.b2Roids.append(roid)

    def explode(self, x, y, z, color, count, lifespan=100):
        p = Particles(count=count, 
                      center=[x,y,z], 
                      color=color, 
                      lifespan=lifespan)
        p.explode(speed=0.1)
        self.particles.append(p)


    def on_draw(self):
        if not self.redraw:
            return
        self.redraw = False
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
        camx = self.b2Moon.body.position.x + self.camera.dist * cos(self.camera.yaw) * cos(self.camera.pitch)
        camy = self.camera.dist * sin(self.camera.pitch)
        camz = self.b2Moon.body.position.y + self.camera.dist * sin(self.camera.yaw) * cos(self.camera.pitch)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, self.al.width/float(self.al.height), 0.1, 20000.0)
        gluLookAt(camx, camy, camz, 
                  self.b2Moon.body.position.x, 
                  self.b2Moon.radius * 8.0, 
                  self.b2Moon.body.position.y, 
                  0.0, 1.0, 0.0)

        glMatrixMode(GL_MODELVIEW)

        # Draw Earth
        glLoadIdentity()
        glTranslatef(self.b2Earth.body.position.x, 0, self.b2Earth.body.position.y)
        glScalef(self.b2Earth.radius, self.b2Earth.radius, self.b2Earth.radius)
        # glRotatef(self.earth.rotation, self.earth.rotation_axis[0], 
        #           self.earth.rotation_axis[1], self.earth.rotation_axis[2])
        glBindTexture(GL_TEXTURE_2D, self.earthTexture.id)
        self.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Moon
        glLoadIdentity()
        glTranslatef(self.b2Moon.body.position.x, 0, self.b2Moon.body.position.y)
        glScalef(self.b2Moon.radius, self.b2Moon.radius, self.b2Moon.radius)
        glRotatef(-self.b2Moon.body.angle*32.0, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, self.moonTexture.id)
        self.sphereGeometry.draw(GL_TRIANGLES)

        # Draw Roids
        for roid in self.b2Roids:
            glLoadIdentity()
            glTranslatef(roid.body.position.x, 0, roid.body.position.y)
            glScalef(roid.radius, roid.radius, roid.radius)
            glRotatef(-roid.body.angle*32.0, 0, 1, 0)
            glBindTexture(GL_TEXTURE_2D, self.roidTexture.id)
            self.roidGeometry.draw(GL_TRIANGLES)

        # Draw Space
        glLoadIdentity()
        glTranslatef(camx, camy, camz)
        glScalef(19000,19000,19000)
        glBindTexture(GL_TEXTURE_2D, self.spaceTexture.id)
        glDisable(GL_LIGHTING)
        glCullFace(GL_FRONT)
        self.sphereGeometry.draw(GL_TRIANGLES)
        glCullFace(GL_BACK)
        glEnable(GL_LIGHTING)

        # Draw Particles
        glLoadIdentity()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)                                             
        glPointSize(1.0)
        for particle in self.particles:
            particle.particles.draw(GL_POINTS)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)

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

    def update(self, dt):
        self.redraw = True
        self.total_time += dt
        numroids = int(self.total_time/10) + 3
        while len(self.b2Roids) < numroids:
            self.addRoid()
        dirForce = numpy.zeros(2)
        forward = -numpy.array([cos(self.camera.yaw), sin(self.camera.yaw)])
        forward /= numpy.linalg.norm(forward)
        right = numpy.array([cos(self.camera.yaw - pi/2), sin(self.camera.yaw - pi/2)])
        right /= numpy.linalg.norm(right)
        speed = 0.2
        if key.W in self.keys:
            dirForce += forward * speed
        if key.S in self.keys:
            dirForce -= forward * speed
        if key.A in self.keys:
            dirForce -= right * speed
        if key.D in self.keys:
            dirForce += right * speed
        self.b2Moon.body.ApplyImpulse(b2Vec2(list(dirForce)), self.b2Moon.body.position)
        for roid in self.b2Roids:
            er = numpy.array(self.b2Earth.body.position.tuple())
            rr = numpy.array(roid.body.position.tuple())
            d = er - rr
            d /= numpy.linalg.norm(d)
            d *= 0.001
            roid.body.ApplyImpulse(b2Vec2(list(d)), roid.body.position)
        self.world.Step(1.0, 10, 8)
        for roid in self.b2Roids[:]:
            if roid.dead:
                self.b2Roids.remove(roid)
                self.world.DestroyBody(roid.body)
        for particle in self.particles[:]:
            particle.update()
            if particle.dead:
                self.particles.remove(particle)

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


