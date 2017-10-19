from lib import Move, Rotate, Element, Slab, SlabSet, Material

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

BL_BOK = SZ_BOKPRZOD * PROPORCJA

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
        mat = Material(0xffff00)
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



    def render(self):
        for szuflada in self.szuflady:
            szuflada.render()



