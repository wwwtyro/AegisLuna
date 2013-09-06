from math import pi, sin, cos, sqrt
import random
import numpy
from numpy.linalg import norm
import perlin
import pyglet
from pyglet.gl import *

simplex = perlin.SimplexNoise()

def vec(*args):
    return (GLfloat * len(args))(*args)

def unit(v):
    return v/numpy.linalg.norm(v)

def spherePoint(yaw, pitch):
    x = cos(yaw) * cos(pitch)
    y = sin(pitch)
    z = sin(yaw) * cos(pitch)
    u = yaw / (2*pi)
    v = (pitch + pi/2) / pi
    return x, y, z, u, v


def buildSphere(resolution):
    vertices = []
    uvs = []
    normals = []
    wedges = resolution
    slices = resolution/2
    pitch_step = pi/slices
    yaw_step = 2*pi/wedges
    u_step = 1.0/wedges
    v_step = 1.0/slices
    for w in range(wedges):
        for s in range(slices):
            pitch = pi/2 - s*pitch_step
            yaw = w*yaw_step
            x0, y0, z0, u0, v0 = spherePoint(yaw, pitch)
            x1, y1, z1, u1, v1 = spherePoint(yaw + yaw_step, pitch)
            x2, y2, z2, u2, v2 = spherePoint(yaw + yaw_step, pitch - pitch_step)
            x3, y3, z3, u3, v3 = spherePoint(yaw, pitch - pitch_step)
            vertices.extend((x3, y3, z3))
            vertices.extend((x0, y0, z0))
            vertices.extend((x2, y2, z2))
            vertices.extend((x0, y0, z0))
            vertices.extend((x1, y1, z1))
            vertices.extend((x2, y2, z2))
            normals.extend((x3, y3, z3))
            normals.extend((x0, y0, z0))
            normals.extend((x2, y2, z2))
            normals.extend((x0, y0, z0))
            normals.extend((x1, y1, z1))
            normals.extend((x2, y2, z2))
            uvs.extend((u3, v3))
            uvs.extend((u0, v0))
            uvs.extend((u2, v2))
            uvs.extend((u0, v0))
            uvs.extend((u1, v1))
            uvs.extend((u2, v2))
    return pyglet.graphics.vertex_list(len(vertices)/3, ('v3f', vertices), ('n3f', normals), ('t2f', uvs))


def asteroidPoint(yaw, pitch):
    D = 0.1
    R = 1.0
    x = cos(yaw) * cos(pitch)
    y = sin(pitch)
    z = sin(yaw) * cos(pitch)
    r = simplex.noise3(x*R, y*R, z*R) * D + (1.0 - D)
    x *= r
    y *= r
    z *= r
    delta = 0.01
    xdy = cos(yaw + delta) * cos(pitch)
    ydy = sin(pitch)
    zdy = sin(yaw+delta) * cos(pitch)
    rdy = simplex.noise3(xdy*R, ydy*R, zdy*R) * D + (1.0 - D)
    xdy *= rdy
    ydy *= rdy
    zdy *= rdy
    dy = numpy.array([xdy - x, ydy - y, zdy - z])
    dy /= numpy.linalg.norm(dy)
    xdp = cos(yaw) * cos(pitch + delta)
    ydp = sin(pitch + delta)
    zdp = sin(yaw) * cos(pitch + delta)
    rdp = simplex.noise3(xdp*R, ydp*R, zdp*R) * D + (1.0 - D)
    xdp *= rdp
    ydp *= rdp
    zdp *= rdp
    dp = numpy.array([xdp - x, ydp - y, zdp - z])
    dp /= numpy.linalg.norm(dp)
    n = numpy.cross(dp, dy)
    u = yaw / (2*pi)
    v = (pitch + pi/2) / pi
    return x, y, z, u, v, n[0], n[1], n[2]


def buildAsteroid(resolution):
    vertices = []
    uvs = []
    normals = []
    wedges = resolution
    slices = resolution/2
    pitch_step = pi/slices
    yaw_step = 2*pi/wedges
    u_step = 1.0/wedges
    v_step = 1.0/slices
    for w in range(wedges):
        for s in range(slices):
            pitch = pi/2 - s*pitch_step
            yaw = w*yaw_step
            x0, y0, z0, u0, v0, n0x, n0y, n0z = asteroidPoint(yaw, pitch)
            x1, y1, z1, u1, v1, n1x, n1y, n1z = asteroidPoint(yaw + yaw_step, pitch)
            x2, y2, z2, u2, v2, n2x, n2y, n2z = asteroidPoint(yaw + yaw_step, pitch - pitch_step)
            x3, y3, z3, u3, v3, n3x, n3y, n3z = asteroidPoint(yaw, pitch - pitch_step)
            vertices.extend((x3, y3, z3))
            vertices.extend((x0, y0, z0))
            vertices.extend((x2, y2, z2))
            vertices.extend((x0, y0, z0))
            vertices.extend((x1, y1, z1))
            vertices.extend((x2, y2, z2))
            normals.extend((n3x, n3y, n3z))
            normals.extend((n0x, n0y, n0z))
            normals.extend((n2x, n2y, n2z))
            normals.extend((n0x, n0y, n0z))
            normals.extend((n1x, n1y, n1z))
            normals.extend((n2x, n2y, n2z))
            uvs.extend((u3, v3))
            uvs.extend((u0, v0))
            uvs.extend((u2, v2))
            uvs.extend((u0, v0))
            uvs.extend((u1, v1))
            uvs.extend((u2, v2))
    return pyglet.graphics.vertex_list(len(vertices)/3, ('v3f', vertices), ('n3f', normals), ('t2f', uvs))

def buildCircle(color):
    vertices = []
    colors = []
    for theta in range(360):
        t = 2*pi * theta/360.0
        vertices.extend([cos(t), 0, sin(t)])
        colors.extend(color)
    return pyglet.graphics.vertex_list(len(vertices)/3, ('v3f', vertices), ('c4f', colors))


class Particles:

    def __init__(self, count, center=[0,0,0], color=[1,1,1], lifespan=100):
        self.age = 0
        self.count = count
        self.lifespan = lifespan
        self.dead = False
        self.center = center
        self.vertices = numpy.zeros((count,3)) + center
        self.velocity = numpy.zeros((count,3))
        self.colors = numpy.array((color + [1]) * count).reshape((count, 4))
        self.particles = pyglet.graphics.vertex_list(count, ('v3f/stream', self.vertices.ravel().tolist()), ('c4f/stream', self.colors.ravel().tolist()))

    def explode(self, velocity, spread):
        if velocity is None:
            velocity = numpy.zeros(3)
        else:
            if len(velocity) == 2:
                velocity = numpy.array([velocity[0], 0.0, velocity[1]])
        self.velocity = numpy.ones((self.count,3))*velocity + numpy.random.normal(scale=spread, size=(self.count, 3))

    def update(self):
        if self.age == self.lifespan and self.lifespan > 0:
            self.dead = True
            return
        if self.lifespan > 0:
            self.age += 1
            alpha = 1.0 - float(self.age)/self.lifespan
            tempcolors = self.colors * numpy.array([1,1,1,alpha])
            self.particles.colors = tempcolors.ravel().tolist()
        self.vertices += self.velocity
        self.particles.vertices = self.vertices.ravel().tolist()

