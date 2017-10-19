import lib
import model
import render

if __name__ == '__main__':
    mebel = model.Calosc()
    renderer = render.Renderer()
    print(model.podsumuj())
    if renderer.init_graphics():
        renderer.render(mebel)
    else:
        print("Renderer init error")