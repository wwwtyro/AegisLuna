from math import pi, sin, cos
import numpy
import perlin
import pyglet
from pyglet.gl import *

simplex = perlin.SimplexNoise()

def RotMatArbAxis(angle, A):
    c = cos(angle)
    s = sin(angle)
    Ax = A[0]
    Ay = A[1]
    Az = A[2]
    row0 = [   c + (1 - c)*Ax**2, (1 - c)*Ax*Ay - s*Az, (1 - c)*Ax*Az + s*Ay]
    row1 = [(1 - c)*Ax*Ay + s*Az,    c + (1 - c)*Ay**2, (1 - c)*Ay*Az - s*Ax]
    row2 = [(1 - c)*Ax*Az - s*Ay, (1 - c)*Ay*Az + s*Ax,    c + (1 - c)*Az**2]
    return numpy.array([row0, row1, row2])

def vec(*args):
    return (GLfloat * len(args))(*args)


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