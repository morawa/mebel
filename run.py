import lib
import model
import render

if __name__ == '__main__':
    szuf = model.Szuflada()
    renderer = render.Renderer()
    print(model.podsumuj())
    if renderer.init_graphics():
        renderer.render(szuf)
    else:
        print("Renderer init error")