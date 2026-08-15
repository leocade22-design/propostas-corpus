"""Gera os três PNGs do ícone do Propostas CORPUS.

    python3 ferramentas-icone.py icons

A folha de papel é a forma principal — é o que se reconhece a 48px na tela
inicial. A Corpus entra como selo no canto inferior da folha, e o selo é a
MARCA DE VERDADE: não um desenho parecido, mas os pixels do logo que já está
dentro de modelos.js, no `word/media/` do modelo da Proposta.

Duas coisas valem registrar, porque custaram tentativa:

1. A cópia do logo que está no modelo do Aceite é degradada — quase toda preta,
   sem o verde. A boa é a do modelo da Proposta (`image2.jpeg`), e é dela que
   sai tanto a marca quanto a cor de fundo.

2. O logo é colado DEPOIS de reduzir o desenho, e não antes. O resto é desenhado
   em 4x e reduzido pra ganhar borda lisa; se o bitmap passasse por esse caminho
   ele seria ampliado 4x e voltaria borrado. No tamanho final o selo tem ~168px
   e a origem tem 115px, então a ampliação é de 1,5x — o suficiente pra
   continuar nítido.

O fundo do selo é branco e o do logo também, então não é preciso recortar nada:
o antialias original do logo se encaixa sozinho no disco.
"""
import base64
import io
import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw

VERDE_FUNDO = (0, 98, 54)      # verde da Corpus, um tom abaixo pra servir de fundo
PAPEL       = (255, 255, 255)
LINHA       = (150, 168, 156)
DOBRA       = (206, 220, 210)

ESC = 4                        # supersampling do que é desenhado
RAIZ = os.path.dirname(os.path.abspath(__file__))


def logo_da_corpus():
    """Tira o logo de dentro de modelos.js — a mesma fonte que os documentos
    usam, então o ícone nunca sai de sincronia com o que é impresso."""
    src = open(os.path.join(RAIZ, "modelos.js"), encoding="utf-8").read()
    m = re.search(r'TPL_P\s*=\s*"([^"]+)"', src)
    if not m:
        raise SystemExit("TPL_P não encontrado em modelos.js")
    docx = zipfile.ZipFile(io.BytesIO(base64.b64decode(m.group(1))))
    img = Image.open(io.BytesIO(docx.read("word/media/image2.jpeg"))).convert("RGB")

    # recorta só a marca: o texto "CORPUS" fica à direita e não entra no ícone
    px = img.load()
    branco = lambda c: c[0] > 195 and c[1] > 195 and c[2] > 195
    fim = 0
    for x in range(img.size[0]):
        if any(not branco(px[x, y]) for y in range(img.size[1])):
            fim = x
        elif fim and x > fim + 5:
            break
    marca = img.crop((0, 0, fim + 2, img.size[1]))

    # centraliza num quadrado branco, pra caber no disco sem deformar
    lado = max(marca.size) + 6
    quadro = Image.new("RGB", (lado, lado), PAPEL)
    quadro.paste(marca, ((lado - marca.size[0]) // 2, (lado - marca.size[1]) // 2))
    return quadro


def folha(d, x, y, w, h, dobra):
    """Folha de papel com o canto superior direito dobrado."""
    d.polygon([(x, y), (x + w - dobra, y), (x + w, y + dobra),
               (x + w, y + h), (x, y + h)], fill=PAPEL)
    d.polygon([(x + w - dobra, y), (x + w, y + dobra), (x + w - dobra, y + dobra)],
              fill=DOBRA)


def desenhar(lado, marca, margem_maskable=0.0):
    L = lado * ESC
    im = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # No maskable o sistema recorta um círculo: o conteúdo recua pro meio e o
    # fundo sangra até a borda.
    if margem_maskable:
        d.rectangle([0, 0, L, L], fill=VERDE_FUNDO)
        util = L * (1 - 2 * margem_maskable)
        ox = oy = L * margem_maskable
    else:
        d.rounded_rectangle([0, 0, L - 1, L - 1], radius=int(L * 0.235), fill=VERDE_FUNDO)
        util = L
        ox = oy = 0

    fw, fh = util * 0.50, util * 0.62
    fx = ox + (util - fw) / 2 - util * 0.035
    fy = oy + (util - fh) / 2 - util * 0.028
    folha(d, fx, fy, fw, fh, util * 0.145)

    # linhas de texto da proposta
    lx, lw = fx + fw * 0.17, fw * 0.66
    ly, esp = fy + fh * 0.34, fh * 0.135
    for fator in (1.0, 1.0, 0.62):
        d.rounded_rectangle([lx, ly, lx + lw * fator, ly + fh * 0.052],
                            radius=fh * 0.026, fill=LINHA)
        ly += esp

    # disco branco do selo, ainda em 4x
    sr = util * 0.205
    scx = fx + fw + util * 0.010
    scy = fy + fh - util * 0.020
    d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=PAPEL)

    pronto = im.resize((lado, lado), Image.LANCZOS)

    # O logo entra só agora, no tamanho final — ver o comentário lá em cima.
    # Vai por uma máscara redonda: o recorte do logo é quadrado e, sem ela, os
    # quatro cantos brancos apareceriam por cima do verde do fundo. A marca é
    # circular, então o que a máscara corta é só o branco de sobra.
    tam = max(8, int(sr / ESC * 2 * 0.82))
    selo = marca.resize((tam, tam), Image.LANCZOS)
    redondo = Image.new("L", (tam * 4, tam * 4), 0)
    ImageDraw.Draw(redondo).ellipse([0, 0, tam * 4 - 1, tam * 4 - 1], fill=255)
    pronto.paste(selo, (int(scx / ESC - tam / 2), int(scy / ESC - tam / 2)),
                 redondo.resize((tam, tam), Image.LANCZOS))
    return pronto


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else "icons"
    marca = logo_da_corpus()
    desenhar(512, marca).save(os.path.join(destino, "icon-512.png"))
    desenhar(192, marca).save(os.path.join(destino, "icon-192.png"))
    desenhar(512, marca, margem_maskable=0.14).save(
        os.path.join(destino, "icon-512-maskable.png"))
    print("ícones gerados em %s — logo de %dpx de origem" % (destino, marca.size[0]))
