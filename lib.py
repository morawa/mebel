from copy import deepcopy


class V3(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return V3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other):
        if isinstance(other, V3):
            return V3(self.x * other.x, self.y * other.y, self.z * other.z)
        else:
            return V3(self.x * other, self.y * other, self.z * other)

    def __mod__(self, other):
        if isinstance(other, V3):
            return V3(self.x % other.x, self.y % other.y, self.z % other.z)
        else:
            return V3(self.x % other, self.y % other, self.z % other)



class Element():
    __clonable_attrs__ = ''
    __reference_attrs__ = ''

    def __init__(self, **kwargs):
        self.translation = V3()
        self.rotation = V3()
        self.params = {}
        for k, v in kwargs.items():
            self.params[k] = v

    def clone(self):
        res = self.__class__()
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

    def rotate(self, ang_x=0.0, ang_y=0.0, ang_z=0.0):
        self.rotation += V3(ang_x, ang_y, ang_z)

    def move(self, d_x=0.0, d_y=0.0, d_z=0.0):
        self.translation += V3(d_x, d_y, d_z)

    def get_renderables(self):
        return [self]


class Material():
    def __init__(self, kolor):
        self.kolor = kolor


class Plane():
    def __init__(self, w, h, translation, rotation, mat):
        self.w = w
        self.h = h
        self.translation = translation
        self.rotation = rotation
        self.mat = mat


class Slab(Element):
    __clonable_attrs__ = 'translation rotation w h th cuts'
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

    def get_renderables(self):
        # TODO: nie obsługujemy wcięć
        res = []
        h_w = self.w / 2.0
        h_h = self.h / 2.0
        h_th = self.th / 2.0
        t = self.translation
        r = self.rotation
        r_ud = r + V3(x=90.0)
        r_ud %= 360.0
        r_lr = r + V3(y=90.0)
        r_lr %= 360.0
        res.append(Plane(self.w, self.h, t+V3(z=h_th), r, self.mat))
        res.append(Plane(self.w, self.h, t+V3(z=-h_th), r, self.mat))
        res.append(Plane(self.h, self.th, t+V3(x=h_w), r_lr, self.mat))
        res.append(Plane(self.h, self.th, t+V3(x=-h_w), r_lr, self.mat))
        res.append(Plane(self.w, self.th, t+V3(y=h_h), r_ud, self.mat))
        res.append(Plane(self.w, self.th, t+V3(y=-h_h), r_ud, self.mat))
        return res


class SlabSet(Element):
    def __init__(self, **kwargs):
        Element.__init__(self, **kwargs)
        self.slabs = []

    def add_slab(self, slab):
        self.slabs.append(slab)

    def clone(self):
        res = SlabSet()
        for slab in self.slabs:
            res.add_slab(slab.clone())

    def rotate(self, ang_x=0.0, ang_y=0.0, ang_z=0.0):
        pass  # TODO zmiana położeń każdego elementu odpowiednio, a potem obroty

    def move(self, d_x=0.0, d_y=0.0, d_z=0.0):
        for slab in self.slabs:
            slab.move(d_x, d_y, d_z)

    def get_renderables(self):
        res = []
        for slab in self.slabs:
            res += slab.get_renderables()
        return res
