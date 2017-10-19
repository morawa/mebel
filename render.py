from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os, traceback
from math import *
import lib

# ustawienia

screen_size = [1024, 768]
multisample = 0  # 16

camera_radius_def = 30.0
camera_fov = 20.0
spacing = 2.0

camera_rot_def = [150.0, 35.0]
camera_center_def = [0.0, 0.0, 0.0]

camera_radius = camera_radius_def
camera_rot = list(camera_rot_def)
camera_center = list(camera_center_def)


# funkcyjki pomocnicze zerżnięte z tic-tac-toe 3d


def roundint(num): return int(round(num))


def set_view_2D(rect):
    glViewport(*list(map(roundint, rect)))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(rect[0], rect[0] + rect[2], rect[1], rect[1] + rect[3], -1.0, 1.0);
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def set_view_3D(rect):
    # ustawia obszar widzenia - x, y, szer, wys
    glViewport(*list(map(roundint, rect)))
    # wybór stosu operacji, do którego będą dokładane od teraz macierze
    # GL_MODELVIEW - stos widoku modeli
    # GL_PROJECTION - stos widoku projekcji
    # GL_TEXTURE - stos teksturowania
    # GL_COLOR - stos wyliczeń kolorów
    glMatrixMode(GL_PROJECTION)
    # zamienia (?) bieżącą macież na identycznościową, reset stosu?
    glLoadIdentity()
    if True:
        # ustawia projekcję w perspektywie (załadowanie macierzy)
        # kąt widzenia (w stopniach), proporcje widoku, odległość obcinania z bliska, odległość obcinania z daleka
        gluPerspective(camera_fov, float(screen_size[0]) / float(screen_size[1]), 0.1, 10000.0)
    else: # wykorzystać do widoku 2D
        # ustawia widok prostopadły
        # (przycinanie) lewy, prawy, dolny, górny, obcinanie z bliska, obcinanie z daleka
        glOrtho(-10.0, 10.0, -10.0, 10.0, -100.0, 100.0);
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def createAndCompileShader(type,source):
    shader=glCreateShader(type)
    glShaderSource(shader,source)
    glCompileShader(shader)

    # get "compile status" - glCompileShader will not fail with
    # an exception in case of syntax errors

    result=glGetShaderiv(shader,GL_COMPILE_STATUS)

    if (result!=1): # shader didn't compile
        raise Exception("Couldn't compile shader\nShader compilation Log:\n"+glGetShaderInfoLog(shader))
    return shader

vertex_shader=createAndCompileShader(GL_VERTEX_SHADER,"""
varying vec3 v;
varying vec3 N;

void main(void)
{

   v = gl_ModelViewMatrix * gl_Vertex;
   N = gl_NormalMatrix * gl_Normal;

   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

}
""");

fragment_shader=createAndCompileShader(GL_FRAGMENT_SHADER,"""
varying vec3 N;
varying vec3 v;

void main(void)
{
   vec3 L = gl_LightSource[0].position.xyz-v;

   // "Lambert's law"? (see notes)
   // Rather: faces will appear dimmer when struck in an acute angle
   // distance attenuation

   float Idiff = max(dot(normalize(L),N),0.0)*pow(length(L),-2.0); 

   gl_FragColor = vec4(0.5,0,0.5,1.0)+ // purple
                  vec4(1.0,1.0,1.0,1.0)*Idiff; // diffuse reflection
}
""");

program=glCreateProgram()
glAttachShader(program,vertex_shader)
glAttachShader(program,fragment_shader)
glLinkProgram(program)

# try to activate/enable shader program
# handle errors wisely

try:
    #glUseProgram(program)
    pass
except OpenGL.error.GLError:
    print(glGetProgramInfoLog(program))
    raise



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
        # ustawiamy pygame'a i okno
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
        # ustawiamy samego opengla
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_2D)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_AMBIENT, (10.4, 0.4, 0.2, 0.1))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

        glClearDepth(1.0)

        return True

    def set_camera(self, rect=[0, 0, screen_size[0], screen_size[1]], cen=camera_center, rot=camera_rot, rad=camera_radius):
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

    def set_light(self, t):
        ld = [sin(t / 16.0) * 4.0, sin(t / 20.0) * 4.0, cos(t / 16.0) * 4.0]

        # pass data to fragment shader

        glLightfv(GL_LIGHT0, GL_POSITION, [ld[0], ld[1], ld[2]]);

    def draw_surf(self, surf, x, y):
        w, h = surf.get_size()
        data = pygame.image.tostring(surf, "RGBA", 1)
        glRasterPos2f(x, y)
        glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glRasterPos2i(0, 0)

    def render_2d(self, model):
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

        glColor4f(c[0],c[1],c[2], 1.0)
        # self.draw_surf(surf, loc[0], loc[1])

    def render_scene(self, model, iter):
        # czyszczenie buforów: COLOR, DEPTH, ACCUM, STENCIL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # coś z własciwego rysowania planszy, w tym setView3d i ustawienie punktu widzenia
        self.set_camera(rad=4000.0, rot=[iter, 25 * sin(iter/100)])
        # self.set_light(iter)
        model.render()

        self.render_2d(model)
        # widok 2D - do rysowania napisów itp

    def render(self, model):
        clock = pygame.time.Clock()
        iter = 0
        while True:
            if not handle_pygame_input(): break
            # state_module.state.draw()
            model.set_frame(iter)
            self.render_scene(model, iter)
            iter+= 1
            pygame.display.flip()

            clock.tick(30)
        pygame.quit()


        # ruch kamery, wysyłanie keyframe'ów do modelu itp
