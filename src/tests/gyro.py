import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import zmq
import json

def quaternion_to_matrix(quaternion):
    w, x, y, z = quaternion
    Nq = w*w + x*x + y*y + z*z
    if Nq < 1e-8:
        return np.identity(4)
    s = 2.0/Nq
    X = x*s
    Y = y*s
    Z = z*s
    wX = w*X; wY = w*Y; wZ = w*Z
    xX = x*X; xY = x*Y; xZ = x*Z
    yY = y*Y; yZ = y*Z
    zZ = z*Z
    return np.array(
           [[ 1.0-(yY+zZ), xY-wZ, xZ+wY, 0.0],
            [ xY+wZ, 1.0-(xX+zZ), yZ-wX, 0.0],
            [ xZ-wY, yZ+wX, 1.0-(xX+yY), 0.0],
            [ 0.0, 0.0, 0.0, 1.0]])

def draw_parallelepiped(length=1.0, width=1.0, height=1.0):
    vertices = [
        [-length/2, -width/2, -height/2],
        [length/2, -width/2, -height/2],
        [length/2, width/2, -height/2],
        [-length/2, width/2, -height/2],
        [-length/2, -width/2, height/2],
        [length/2, -width/2, height/2],
        [length/2, width/2, height/2],
        [-length/2, width/2, height/2]
    ]

    colors = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1)
    ]

    faces = [
        (0, 1, 2, 3),
        (1, 5, 6, 2),
        (5, 4, 7, 6),
        (4, 0, 3, 7),
        (3, 2, 6, 7),
        (4, 5, 1, 0)
    ]

    texture_coordinates = [
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1)
    ]

    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    for i, face in enumerate(faces):
        glBegin(GL_QUADS)
        glColor3fv(colors[i])
        for j, vertex in enumerate(face):
            glTexCoord2fv(texture_coordinates[j])
            glVertex3fv(vertices[vertex])
        glEnd()

    glDisable(GL_TEXTURE_2D)

def main():
    global quaternion
    quaternion = {"quat_w":1, "quat_x":0, "quat_y":0, "quat_z":0}

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -10)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://192.168.1.52:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        message = socket.recv_string()
        quaternion = json.loads(message)

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        matrix = quaternion_to_matrix([quaternion["quat_w"], quaternion["quat_x"], quaternion["quat_y"], quaternion["quat_z"]])
        glMultMatrixf(matrix.T)
        draw_parallelepiped()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

