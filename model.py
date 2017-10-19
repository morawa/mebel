from lib import Move, Rotate, Element, Slab, SlabSet, Material
from math import sin, cos, radians

SZ_SZER = 300.0
SZ_WYS = 240.0
SZ_GL = 530.0

SZ_GR_SC = 8.0

PL_GR = 12.0

# szer : wys = 5 : 4

PROPORCJA = 5.0 / 4.0

# suma szerokości i głębokości szuflady
SZ_BOKPRZOD = SZ_SZER + SZ_WYS

# długość boku blatu

BL_BOK = 2 * SZ_GL # * PROPORCJA

# wysokość nóżek (części wystającej pod blatem)

PODBLAT_WYS = SZ_WYS / PROPORCJA

# wysokość od podłogi do wierzchu blatu

MEBEL_WYS = PODBLAT_WYS + PL_GR + SZ_WYS + PL_GR


def podsumuj():
    lines = [
        "Całkowita wysokość: %dmm" % MEBEL_WYS,
        "Szerokość blatu: %dmm" % BL_BOK
    ]
    return '\n'.join(lines)


class Szuflada(SlabSet):
    def __init__(self):
        SlabSet.__init__(self)
        mat = Material(0.7, 0.4, 0.2, 0.99)
        dno = Slab(w=SZ_SZER-SZ_GR_SC, h=SZ_GL-SZ_GR_SC, th=SZ_GR_SC, mat=mat)
        dno.do(Move(y=-(SZ_WYS / 2 - SZ_GR_SC)))
        dno.do(Rotate(90, x=1))
        front = Slab(w=SZ_SZER, h=SZ_WYS, th=SZ_GR_SC, mat=mat)
        tyl = front.clone()
        front.do(Move(z=(SZ_GL/2 - SZ_GR_SC/2)))
        tyl.do(Move(z=-(SZ_GL/2 - SZ_GR_SC/2)))
        lewy_bok = Slab(w=SZ_GL-2*SZ_GR_SC, h=SZ_WYS, th=SZ_GR_SC, mat=mat)
        prawy_bok = lewy_bok.clone()
        lewy_bok.do(Move(x=-(SZ_SZER/2-SZ_GR_SC/2)))
        prawy_bok.do(Move(x=(SZ_SZER/2-SZ_GR_SC/2)))
        lewy_bok.do(Rotate(90, y=1))
        prawy_bok.do(Rotate(90, y=1))
        self.add_slab(dno)
        self.add_slab(front)
        self.add_slab(tyl)
        self.add_slab(lewy_bok)
        self.add_slab(prawy_bok)


class Calosc(Element):
    def __init__(self):
        s1 = Szuflada()
        s2 = s1.clone()
        s3 = s1.clone()
        s4 = s1.clone()
        s2.do(Rotate(90, y=1))
        s3.do(Rotate(180, y=1))
        s4.do(Rotate(270, y=1))
        self.szuflady = [s1, s2, s3, s4]
        for s in self.szuflady:
            s.do(Move(x=SZ_SZER/2, z=SZ_GL/2))
        mat = Material(0.8, 0.5, 0.3, 0.7)
        self.blat = Slab(BL_BOK, BL_BOK, PL_GR, mat)
        self.blat.do(Rotate(90, x=1))
        self.blat.do(Move(z=-SZ_WYS/2-PL_GR/2))
        self.podstawa = Slab(2*SZ_GL, 2*SZ_GL, PL_GR, mat)
        self.podstawa.do(Rotate(90, x=1))
        self.podstawa.do(Move(z=SZ_WYS/2+PL_GR/2))
        n1 = Slab(SZ_GL, SZ_WYS+PL_GR+PODBLAT_WYS, PL_GR, mat)
        n2 = n1.clone()
        n3 = n1.clone()
        n4 = n1.clone()
        self.nogi = [n1, n2, n3, n4]
        n2.do(Rotate(90, y=1))
        n3.do(Rotate(180, y=1))
        n4.do(Rotate(270, y=1))
        for noga in self.nogi:
            noga.do(Move(x=-SZ_GL/2, y=-SZ_WYS/2+PL_GR, z=SZ_SZER+PL_GR/2))

        self.szuflady[2].do(Move())

    def set_frame(self, frame):
        supframe = frame
        wysun = 0
        if supframe % 360 > 180:
            wysun = SZ_GL * (sin(radians(supframe % 360 - 180)))
        self.szuflady[2].operations[-1].z = wysun

    def render(self):
        for szuflada in self.szuflady:
            szuflada.render()
        self.blat.render()
        self.podstawa.render()
        for noga in self.nogi:
            noga.render()



