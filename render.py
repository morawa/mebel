from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os, traceback
from math import *

class Renderer(object):
    def __init__(self):
        pass

    def init_graphics(self):
        pygame.display.init()
        pygame.font.init()
        return True

    def render(self, model):
        primitives = model.get_renderables()
        for p in primitives:
            if isinstance(p, lib.Plane):
                pass # cośtam
                glColor4f(1,1,0,0.5)
                gl_misc.draw_square(projected[0],projected[1],projected[2])

            else:
                raise Exception('Can not render', p.__class__)

    # ruch kamery, wysyłanie keyframe'ów do modelu itp