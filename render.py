from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os, traceback
from math import *
import lib

# ustawienia

screen_size = [800, 600]
multisample = 0  # 16

which_camera = 2
if which_camera == 1:
    camera_radius_def = 15.0
    camera_fov = 45.0
    spacing = 2.0
elif which_camera == 2:
    camera_radius_def = 30.0
    camera_fov = 20.0
    spacing = 2.0
elif which_camera == 3:
    camera_radius_def = 40.0
    spacing = 4.0
camera_rot_def = [150.0, 35.0]  # [170.0,20.0]
camera_center_def = [2.0, 1.5 * spacing, 2.0]

camera_radius = camera_radius_def
camera_rot = list(camera_rot_def)
camera_center = list(camera_center_def)


# funkcyjki pomocnicze zerżnięte z tic-tac-toe 3d

def gl_setup():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_DEPTH_TEST)


def draw_square(x, y, z):
    spacing = 0.4
    glBegin(GL_QUADS)
    glVertex3f(x, spacing * y, z)
    glVertex3f(x + 1, spacing * y, z)
    glVertex3f(x + 1, spacing * y, z + 1)
    glVertex3f(x, spacing * y, z + 1)
    glEnd()


def draw_plane(plane):

    glBegin(GL_QUADS)
    glVertex3f(plane.translation.x, plane.translation.y, 0)
    glVertex3f(plane.translation.x+plane.w, plane.translation.y, 0)
    glVertex3f(plane.translation.x+plane.w, plane.translation.y+plane.h, 0)
    glVertex3f(plane.translation.x, plane.translation.y+plane.h, 0)
    glEnd()


def _rndint(num): return int(round(num))


def set_view_2D(rect):
    glViewport(*list(map(_rndint, rect)))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(rect[0], rect[0] + rect[2], rect[1], rect[1] + rect[3], -1.0, 1.0);
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def set_view_3D(rect):
    # ustawia obszar widzenia - x, y, szer, wys
    glViewport(*list(map(_rndint, rect)))
    # wybór stosu operacji, do którego będą dokładane od teraz macierze
    # GL_MODELVIEW - stos widoku modeli
    # GL_PROJECTION - stos widoku projekcji
    # GL_TEXTURE - stos teksturowania
    # GL_COLOR - stos wyliczeń kolorów
    glMatrixMode(GL_PROJECTION)
    # zamienia (?) bieżącą macież na identycznościową, reset stosu?
    glLoadIdentity()
    if which_camera < 3:
        # ustawia projekcję w perspektywie (załadowanie macierzy)
        # kąt widzenia (w stopniach), proporcje widoku, odległość obcinania z bliska, odległość obcinania z daleka
        gluPerspective(camera_fov, float(screen_size[0]) / float(screen_size[1]), 0.1, 1000.0)
    else:
        # ustawia widok prostopadły
        # (przycinanie) lewy, prawy, dolny, górny, obcinanie z bliska, obcinanie z daleka
        glOrtho(-10.0, 10.0, -10.0, 10.0, -100.0, 100.0);
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def set_camera(rect=[0, 0, screen_size[0], screen_size[1]], cen=camera_center, rot=camera_rot, rad=camera_radius):
    set_view_3D(rect)

    camera_pos = [
        cen[0] + rad * cos(radians(rot[0])) * cos(radians(rot[1])),
        cen[1] + rad * sin(radians(rot[1])),
        cen[2] + rad * sin(radians(rot[0])) * cos(radians(rot[1]))
    ]
    # pozycja oka, pozycja punktu na który patrzymy, kierunek wektora do góry
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],
        cen[0], cen[1], cen[2],
        0, 1, 0
    )


keys_pressed = mouse_buttons = mouse_position = mouse_rel = None


def handle_pygame_input():
    global keys_pressed, mouse_buttons, mouse_position, mouse_rel

    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = list(pygame.mouse.get_pos())
    mouse_position[1] = screen_size[1] - mouse_position[1]
    mouse_rel = pygame.mouse.get_rel()

    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        elif event.type == KEYDOWN:
            if event.unicode == 'q':
                return False
            print(event)
            #    if not self._process_keydown(event): return False
            # elif event.type == MOUSEBUTTONDOWN:
            #    if not self._process_mousebuttondown(event): return False
    return True


class Renderer(object):
    def __init__(self):
        pass

    def init_graphics(self):
        pygame.display.init()
        pygame.font.init()
        icon = pygame.Surface((1, 1))
        icon.set_alpha(0)
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Ławoszafka")
        if multisample:
            pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, multisample)
        pygame.display.set_mode(screen_size, OPENGL | DOUBLEBUF)
        gl_setup()
        return True

    def draw_surf(self, surf, x, y):
        w, h = surf.get_size()
        data = pygame.image.tostring(surf, "RGBA", 1)
        glRasterPos2f(x, y)
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glRasterPos2i(0, 0)

    def render_scene(self, model, iter):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # coś z własciwego rysowania planszy, w tym setView3d i ustawienie punktu widzenia
        set_camera(rad=0.1*iter)

        glClear(GL_DEPTH_BUFFER_BIT)

        glColor4f(1, 1, 0, 1)
        draw_square(1, 20, 10)
        glColor4f(0.01*iter % 1.0, 0, 1, 1)

        model.render()

        # widok 2D - do rysowania napisów itp
        set_view_2D([0, 0, screen_size[0], screen_size[1]])
        font36 = pygame.font.SysFont("Times New Roman", 36)
        text = "Bla bla bla"
        surf = font36.render(text, True, (255, 255, 255))
        loc = [2.0, 2.0]
        c = [0.6, 0.6, 0.6, 1.0]
        if mouse_position[0] > loc[0] and mouse_position[0] < loc[0] + surf.get_width():
            if mouse_position[1] > loc[1] and mouse_position[1] < loc[1] + surf.get_height():
                # self.hovering = index
                c = [0.8, 0.8, 0.0, 1.0]
        c = list(map(lambda x: int(round(255.0 * x)), c))

        surf = font36.render(text, True, c).convert_alpha()

        # glColor4f(c[0],c[1],c[2], 1.0)
        glColor4f(0, 1, 1, 1)
        self.draw_surf(surf, loc[0], loc[1])

    def render(self, model):

        clock = pygame.time.Clock()
        iter = 0
        while True:
            if not handle_pygame_input(): break
            # state_module.state.draw()
            self.render_scene(model, iter)
            iter+= 1
            pygame.display.flip()

            clock.tick(30)
        pygame.quit()


        # ruch kamery, wysyłanie keyframe'ów do modelu itp
