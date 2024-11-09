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

def draw_axes(length=1.0):
    glBegin(GL_LINES)
    glColor3f(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(length,0,0)
    glColor3f(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,length,0)
    glColor3f(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,length)
    glEnd()

def main():
    global quaternion
    quaternion = {"w":1, "x":0, "y":0, "z":0}

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -10)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5555")
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
        matrix = quaternion_to_matrix([quaternion["w"], quaternion["x"], quaternion["y"], quaternion["z"]])
        glMultMatrixf(matrix.T)
        draw_axes()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

