"""Ícone do Propostas CORPUS.

A folha de papel continua sendo a forma principal — é o que se reconhece a 48px
na tela inicial, e o Léo pediu pra manter o formato de hoje. A referência à
Corpus entra como selo no canto: os dois arcos em "C" da marca, verde por fora
e escuro por dentro, num disco branco que os separa do fundo.

Desenha em 4x e reduz: é assim que se consegue borda lisa sem antialias nativo.
"""
from PIL import Image, ImageDraw

VERDE      = (0, 113, 62)      # #00713E — amostrado do logo dentro do modelo
VERDE_FUNDO= (0, 98, 54)
ESCURO     = (32, 28, 25)      # #201C19 — o arco interno da marca
PAPEL      = (255, 255, 255)
LINHA      = (150, 168, 156)
DOBRA      = (206, 220, 210)

ESC = 4  # supersampling


def squircle(d, caixa, raio, cor):
    """Quadrado de cantos bem arredondados, no espírito do ícone de hoje."""
    d.rounded_rectangle(caixa, radius=raio, fill=cor)


def folha(d, x, y, w, h, dobra):
    """Folha com o canto superior direito dobrado."""
    d.polygon([(x, y), (x + w - dobra, y), (x + w, y + dobra),
               (x + w, y + h), (x, y + h)], fill=PAPEL)
    # a dobra em si, um triângulo mais escuro
    d.polygon([(x + w - dobra, y), (x + w, y + dobra), (x + w - dobra, y + dobra)],
              fill=DOBRA)


def marca_corpus(d, cx, cy, r):
    """Os dois arcos em "C" da marca. No PIL o ângulo começa no leste e cresce
    no sentido horário (o eixo y aponta pra baixo), então:
      · o arco VERDE é o de fora e abre em cima à esquerda  (vão em 190°–260°)
      · o arco ESCURO é o de dentro e abre embaixo à direita (vão em 10°–80°)
    Os dois vãos em diagonais opostas são o que dá o giro do logo. Entre eles e
    no centro sobra branco — é isso que impede a marca de virar um borrão quando
    o ícone encolhe pra 48px."""
    gExt = r * 0.26
    rExt = r * 0.86
    d.arc([cx - rExt, cy - rExt, cx + rExt, cy + rExt],
          start=260, end=550, fill=VERDE, width=max(1, int(gExt)))

    gInt = r * 0.25
    rInt = r * 0.52
    d.arc([cx - rInt, cy - rInt, cx + rInt, cy + rInt],
          start=80, end=370, fill=ESCURO, width=max(1, int(gInt)))


def desenhar(lado, margem_maskable=0.0):
    L = lado * ESC
    im = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # No maskable o sistema recorta um círculo: tudo que importa fica no meio,
    # e o fundo tem que sangrar até a borda.
    if margem_maskable:
        d.rectangle([0, 0, L, L], fill=VERDE_FUNDO)
        util = L * (1 - 2 * margem_maskable)
        ox = oy = L * margem_maskable
    else:
        squircle(d, [0, 0, L - 1, L - 1], int(L * 0.235), VERDE_FUNDO)
        util = L
        ox = oy = 0

    # ---- folha
    fw = util * 0.50
    fh = util * 0.62
    fx = ox + (util - fw) / 2 - util * 0.035
    fy = oy + (util - fh) / 2 - util * 0.028
    folha(d, fx, fy, fw, fh, util * 0.145)

    # ---- linhas de texto da proposta
    lx = fx + fw * 0.17
    lw = fw * 0.66
    esp = fh * 0.135
    ly = fy + fh * 0.34
    for i, fator in enumerate((1.0, 1.0, 0.62)):
        d.rounded_rectangle([lx, ly, lx + lw * fator, ly + fh * 0.052],
                            radius=fh * 0.026, fill=LINHA)
        ly += esp

    # ---- selo da Corpus, encostado no canto inferior direito da folha
    sr = util * 0.175
    scx = fx + fw + util * 0.010
    scy = fy + fh - util * 0.020
    d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=PAPEL)
    marca_corpus(d, scx, scy, sr * 0.74)

    return im.resize((lado, lado), Image.LANCZOS)


if __name__ == "__main__":
    import sys
    destino = sys.argv[1] if len(sys.argv) > 1 else "."
    desenhar(512).save(destino + "/icon-512.png")
    desenhar(192).save(destino + "/icon-192.png")
    desenhar(512, margem_maskable=0.14).save(destino + "/icon-512-maskable.png")
    print("gerados em", destino)
