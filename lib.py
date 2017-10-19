from copy import deepcopy
from OpenGL.GL import *
from OpenGL.GLU import *
import random


class Operation(object):
    def do(self):
        raise NotImplementedError()

    def undo(self):
        raise NotImplementedError()


class Move(Operation):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def do(self):
        glTranslate(self.x, self.y, self.z)

    def undo(self):
        glTranslate(-self.x, -self.y, -self.z)


class Rotate(Operation):
    def __init__(self, ang, x=0.0, y=0.0, z=0.0):
        self.ang = float(ang)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def do(self):
        glRotate(self.ang, self.x, self.y, self.z)

    def undo(self):
        glRotate(-self.ang, self.x, self.y, self.z)


class Renderable(object):
    def __init__(self):
        self.operations = []

    def render(self):
        raise NotImplementedError()

    def do_operations(self):
        for oper in self.operations:
            oper.do()

    def undo_operations(self):
        for oper in reversed(self.operations):
            oper.undo()


class Element(Renderable):
    __clonable_attrs__ = ''
    __reference_attrs__ = ''

    def __init__(self, **kwargs):
        Renderable.__init__(self)
        self.mat = kwargs.pop('mat') if 'mat' in kwargs else None
        self.params = {}
        for k, v in kwargs.items():
            self.params[k] = v

    def clone(self):
        res = self.__class__()
        res.operations = deepcopy(self.operations)
        for attr_name in self.__clonable_attrs__.split(' '):
            if attr_name in self.params:
                res.params[attr_name] = deepcopy(self.params[attr_name])
            elif hasattr(self.__dict__, attr_name):
                res.__dict__[attr_name] = deepcopy(self.__dict__[attr_name])
        for attr_name in self.__reference_attrs__.split(' '):
            if attr_name in self.params:
                res.params[attr_name] = self.params[attr_name]
            elif hasattr(self.__dict__, attr_name):
                res.__dict__[attr_name] = self.__dict__[attr_name]
        return res

    def do(self, operation):
        self.operations.append(operation)


class Material():
    def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
        self.color = (r, g, b, a)

    def render(self):
        glColor4f(*self.color)


class Plane(Renderable):
    def __init__(self, w, h, operations=None, mat=None):
        Renderable.__init__(self)
        if operations is not None:
            for oper in operations:
                self.operations.append(oper)
        self.w = w
        self.h = h
        self.mat = mat
        # TODO XX debug
        self.mat = Material(random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0))

    def render(self):
        self.do_operations()
        if self.mat is not None:
            self.mat.render()
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(self.w, 0, 0)
        glVertex3f(self.w, self.h, 0)
        glVertex3f(0, self.h, 0)
        glEnd()
        self.undo_operations()


class Slab(Element):
    __clonable_attrs__ = 'w h th cuts'
    __reference_attrs__ = 'mat'

    def cut_corner(self, corner, radius):
        # w wyjściowym widoku corner=0 to prawy górny róg, potem zgodnie ze wskazówkami zegara
        self.cuts[corner] = radius

    def __init__(self, w=0.0, h=0.0, th=0.0, mat=None):
        Element.__init__(self)
        self.w = w
        self.h = h
        self.th = th
        self.mat = mat
        self.cuts = {}
        h_w = self.w / 2.0
        h_h = self.h / 2.0
        h_th = self.th / 2.0
        self.planes = [
            Plane(self.w, self.h, [Move(z=h_th)]),
            Plane(self.w, self.h, [Move(z=-h_th)]),
            Plane(self.h, self.th, [Rotate(90, x=1), Move(x=-h_w)]),
            Plane(self.h, self.th, [Rotate(90, x=1), Move(x=h_w)]),
            Plane(self.w, self.th, [Rotate(90, y=1), Move(y=-h_h)]),
            Plane(self.w, self.th, [Rotate(90, y=1), Move(y=h_h)])
        ]

    def render(self):
        # TODO: nie obsługujemy wcięć
        self.do_operations()
        if self.mat is not None:
            self.mat.render()
        for plane in self.planes:
            plane.render()
        self.undo_operations()


class SlabSet(Element):
    def __init__(self, **kwargs):
        Element.__init__(self, **kwargs)
        self.slabs = []

    def add_slab(self, slab):
        self.slabs.append(slab)

    def clone(self):
        res = Element.clone(self)
        for slab in self.slabs:
            res.add_slab(slab.clone())

    def render(self):
        self.do_operations()
        if self.mat is not None:
            self.mat.render()
        for slab in self.slabs:
            slab.render()
        self.undo_operations()
